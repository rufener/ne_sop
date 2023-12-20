from pathlib import Path, PurePath


class Utils(object):

    @classmethod
    def set_model_record(cls, record, params):
        """
        Set model record
        """
        atts = cls.get_model_record_attributes(record)

        for att in atts:
            if att != 'affaire_doc_file':
                val = params[att] if att in params else getattr(record, att)

                # Check boolean
                if val == 'true':
                    val = True
                if val == 'false':
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
            filepath_ = PurePath( f'_{count}.'.join(str(filepath).rsplit('.', 1)) )
        return filepath_
    
    @classmethod
    def get_upload_path(cls, instance, filename):
        return PurePath(str(instance.item.created.year), instance.item.number, filename)
    
    @classmethod
    def get_next_documentVersion(cls, DocumentModel, data):
        print(data)
        documents = DocumentModel.objects.filter(
            item=data['item'],
            template=data['template']
        ).all().order_by("-version")

        version = 1
        if len(documents) > 0:
            version = documents[0].version + 1
        
        return version

