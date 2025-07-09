from pathlib import Path, PurePath
from django.http import HttpResponse
from icalendar import Calendar, Event as IcsEvent
from datetime import datetime, timedelta
from html.parser import HTMLParser

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import loader

import os


class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_parts = []

    def handle_data(self, data):
        self.text_parts.append(data)

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "div":
            self.text_parts.append("\n")

    def get_text(self):
        return ''.join(self.text_parts)


class Utils(object):
    @classmethod
    def set_model_record(cls, record, params):
        """
        Set model record
        """
        atts = cls.get_model_record_attributes(record)

        for att in atts:
            if att != "affaire_doc_file":
                val = params[att] if att in params else getattr(record, att)

                # Check boolean
                if val == "true":
                    val = True
                if val == "false":
                    val = False
                if val == "null" or val == "":
                    val = None

                setattr(record, att, val)

        return record

    @classmethod
    def iterateFilename(cls, filepath):
        count = 0
        filepath_ = filepath
        while Path(filepath_).exists():
            count += 1
            filepath_ = PurePath(f"_{count}.".join(str(filepath).rsplit(".", 1)))
        return filepath_

    @classmethod
    def get_upload_path(cls, instance, filename):
        return PurePath(str(instance.uuid), filename)
        # return PurePath(str(instance.item.created.year), str(instance.item.id), filename)

    @classmethod
    def removeFile(cls, instance, removeParentDir=False):
        if instance.file:
            instance.file.close()
            print("Deleting existing file:", instance.file.path)
            instance.file.delete(save=False)
        if removeParentDir is True:
            try:
                print("Removing file parent folder:", str(instance.uuid))
                os.rmdir(PurePath(settings.MEDIA_ROOT, str(instance.uuid)))
            except OSError as e:
                print(f"Erreur lors de la suppression du répertoire : {e}")

        return


    @classmethod
    def get_next_documentVersion(cls, DocumentModel, data):
        documents = DocumentModel.objects.filter(item=data["item"], template=data["template"]).all().order_by("-version")

        version = 1
        if len(documents) > 0:
            version = documents[0].version + 1

        return version

    @classmethod
    def itemCreatedNotification(cls, item, request):
        template = loader.get_template("email_create_item_fr-ch.html")

        context = {
            "item_uuid": item.uuid,
            "item_name": item.title,
            "front_url": settings.FRONT_URL,
            "main_service": item.get_entity_lead_name(),
            "support_services": item.get_entity_support_name(),
        }

        user_lead_email = item.get_user_lead_email()
        users_support_email = item.get_users_support_email()

        subject = f"SOP - création de l'OP {item.number}"
        body = template.render(context, request)
        to = user_lead_email if user_lead_email is not None else users_support_email
        cc = users_support_email if to is user_lead_email is not None else None

        cls.sendEmailNotification(subject=subject, body=body, to=to, cc=cc)

    @classmethod
    def itemChangedNotification(cls, item, request):
        template = loader.get_template("email_update_item_fr-ch.html")

        context = {
            "item_uuid": item.uuid,
            "item_name": item.title,
            "front_url": settings.FRONT_URL,
            "main_service": item.get_entity_lead_name(),
            "support_services": item.get_entity_support_name(),
        }

        user_lead_email = item.get_user_lead_email()
        users_support_email = item.get_users_support_email()

        subject = f"SOP - modification de l'OP {item.number}"
        body = template.render(context, request)
        to = user_lead_email if user_lead_email is not None else users_support_email
        cc = users_support_email if to is user_lead_email is not None else None

        cls.sendEmailNotification(subject=subject, body=body, to=to, cc=cc)

    @classmethod
    def itemRemovedNotification(cls, item, request):
        template = loader.get_template("email_delete_item_fr-ch.html")

        context = {
            "item_name": item.title,
        }

        user_lead_email = item.get_user_lead_email()
        users_support_email = item.get_users_support_email()

        subject = f"SOP - suppression de l'OP {item.number}"
        body = template.render(context, request)
        to = user_lead_email if user_lead_email is not None else users_support_email
        cc = users_support_email if to is user_lead_email is not None else None

        cls.sendEmailNotification(subject=subject, body=body, to=to, cc=cc)

    @classmethod
    def itemLateNotification(cls, item, request):
        template = loader.get_template("email_late_item_fr-ch.html")

        context = {
            "item_uuid": item.uuid,
            "item_name": item.title,
            "front_url": settings.FRONT_URL,
            "main_service": item.get_entity_lead_name(),
            "support_services": item.get_entity_support_name(),
        }

        user_lead_email = item.get_user_lead_email()
        users_support_email = item.get_users_support_email()

        subject = f"SOP - retard de traitement de l'OP {item.number}"
        body = template.render(context, request)
        to = user_lead_email if user_lead_email is not None else users_support_email
        cc = users_support_email if to is user_lead_email is not None else None

        cls.sendEmailNotification(subject=subject, body=body, to=to, cc=cc)

    @classmethod
    def sendEmailNotification(cls, subject, body, to, cc=None, bcc=None):
        msg = EmailMultiAlternatives(
            subject=subject,
            body=body,
            from_email="noreply-sop@ne.ch",
            to=to,
            cc=cc,
            bcc=bcc,
        )
        msg.content_subtype = "html"
        msg.send()

    @classmethod
    def auto_adjust_excel_column_width(cls, ws):
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter  # Obtenir la lettre de la colonne
            for cell in col:
                try:
                    actual_max_length = max([len(str(s)) for s in cell.value.split("\n")])
                    if actual_max_length > max_length:
                        max_length = actual_max_length
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)  # Ajouter un peu d'espace
            ws.column_dimensions[column].width = adjusted_width
        return ws

    @staticmethod
    def generate_ics_file(event):
        """
        Generate an ICS file for the provided Event instance
        :param event: An instance of your Event model
        :return: HttpResponse containing the ICS file
        """
        cal = Calendar()
        cal.add('prodid', '-//Neuchâtel//NESOP//EN')
        cal.add('version', '2.0')

        ics_event = IcsEvent()

        # Combine event.date and event.time (or default to midnight if time is None)
        if event.time:
            dtstart = datetime.combine(event.date, event.time)
        else:
            dtstart = datetime.combine(event.date, datetime.min.time())
        ics_event.add('dtstart', dtstart)

        # Default event duration: 1 hour
        dtend = dtstart + timedelta(hours=1)
        ics_event.add('dtend', dtend)

        # Compose a summary (title) from event type and item name if available
        summary = f"OP {event.item.number} - {event.type.name}"
        ics_event.add('summary', summary)

        # Add description and unique identifier
        description = (
            f"Objet politique: {event.item.number} - {event.item.title}\n"
            f"Lien: {settings.FRONT_URL}/#/items/{event.item.uuid}\n"
            f"Date: {event.date.strftime('%d.%m.%Y')} {event.time.strftime('%H:%M:%S') if event.time else ''}\n"
            f"Événement: {event.type.name}\n"
            f"Description: {event.description}"
        )

        ics_event.add('description', description)
        ics_event.add('uid', str(event.uuid))

        if event.created:
            ics_event.add('created', event.created)

        cal.add_component(ics_event)

        response = HttpResponse(cal.to_ical(), content_type='text/calendar; charset=utf-8')
        filename = f"nesop_{event.item.number.replace('.', '')}_{event.date.strftime('%Y%m%d')}.ics"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
