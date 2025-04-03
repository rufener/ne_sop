<template>
    <div class="q-pa-sm q-gutter-sm">

        <!-- BREADCRUMBS NAVIGATION -->
        <q-breadcrumbs style="font-size: 16px">
            <q-breadcrumbs-el label="Calendrier" to="/events" />
        </q-breadcrumbs>

        <!-- SEARCH AND FILTER SECTION -->
        <div class="row q-col-gutter-md q-px-sm q-mt-xs items-center">

            <!-- SEARCH RECORDS FIELD -->
            <div class="col-xs-12 col-sm-8 col-md-6 col-lg-6">
                <q-input bg-color="white" v-model="filter.search" outlined dense placeholder="Rechercher (n° ou titre de l'objet)"> <!-- @update:model-value="query()" -->
                    <template v-slot:prepend>
                        <q-icon name="sym_o_search" />
                    </template>
                    <template v-slot:append>
                        <q-spinner color="blue-grey" :thickness="3" v-if="loading" />
                        <q-btn unelevated dense icon="close" @click="reset">
                            <q-tooltip class="bg-black">Réinitialiser</q-tooltip>
                        </q-btn>
                    </template>
                </q-input>
            </div>

            <!-- ADD NEW RECORD BUTTON -->
            <!--
                <div class="col-xs-12 col-sm-4 col-md-6 col-lg-6">
                    <q-btn padding="sm md" unelevated no-caps color="blue-grey-8" text-color="white" icon="sym_o_add_circle" label="Ajouter" class="q-py-none q-my-none" @click="" to="/events/new">
                        <q-tooltip class="bg-black">Ajouter un nouvel événement</q-tooltip>
                    </q-btn>
                </div>
                -->

        </div>

        <!-- EVENTS TABLE -->
        <q-table title="" :rows="rows" :columns="columns" row-key="id" v-model:pagination="pagination" :loading="loading" @request="onRequest" binary-state-sort class="q-my-lg">
            <!-- TABLE BODY -->
            <template v-slot:body="props">
                <q-tr :props="props">

                    <!-- DATE COLUMN -->
                    <q-td key="date" :props="props">

                        <router-link :to="{
                            name: 'Event',
                            params: {
                                id: props.row.uuid
                            }
                        }">
                            <q-chip clickable square outline color="blue-5" text-color="white" class="q-mx-none">
                                <div class="ellipsis"><b>{{ props.row.date }}</b></div>
                            </q-chip>
                        </router-link>

                    </q-td>

                    <!-- EVENT TYPE COLUMN -->
                    <q-td key="type" :props="props">
                        {{ props.row.type.name }}
                    </q-td>

                    <!-- ITEM COLUMN -->
                    <q-td key="item" :props="props">

                        <router-link :to="{
                            name: 'Item',
                            params: {
                                id: props.row.item.uuid
                            }
                        }">
                            <q-chip clickable square outline color="blue-5" text-color="white" class="q-mx-none">
                                <div class="ellipsis"><b>{{ props.row.item.number }} - {{ props.row.item.title }}</b></div>

                            </q-chip>

                        </router-link>

                    </q-td>

                    <!-- ACTIONS COLUMN -->
                    <q-td key="actions" :props="props">
                        <div class="float-right">
                            <q-btn dense round flat color="grey" name="calendar" :href="`${store.host}/api/event/${props.row.uuid}/download/`" icon="sym_o_calendar_add_on">
                                <q-tooltip class="bg-black">Télécharger fichier calendrier ICS</q-tooltip>
                            </q-btn>
                            <q-btn dense round flat color="red" name="delete" @click="handleDeletion(props.row.uuid)" icon="sym_o_delete">
                                <q-tooltip class="bg-black">Supprimer</q-tooltip>
                            </q-btn>
                        </div>
                    </q-td>
                </q-tr>
            </template>
            <template v-slot:no-data>
                Aucune objet
            </template>
        </q-table>

        <!-- TODO REMOVE/DEV DISPLAY JSON-->
        <div class="bg-light-blue-1 q-my-md q-pa-md" v-if="store.dev">
            <div>store.events</div>
            <div>{{ rows }}</div>
        </div>

        <!-- DELETE DIALOG -->
        <DeleteDialog v-model="dialog.deletion" @delete-event="remove" content="Supprimer définitivement cet événement? L'objet parlementaire lié ne sera pas supprimé." title="Suppression définitive" />

    </div>
</template>

<script>
import { date as mydate } from 'quasar'
import { store } from '../store/store.js'
// import { downloadICS } from '../store/shared.js'
import DeleteDialog from '../components/DeleteDialog.vue'


export default {
    name: 'EventsList',
    components: { DeleteDialog },
    props: { 'title': String },
    emits: [],
    data() {
        return {
            store,
            mydate: mydate,
            selected: null,
            filter: { search: "", item: "" },
            dialog: { deletion: false },
            data: null,
            rows: [],
            loading: false,
            pagination: {
                rowsNumber: 0,
                sortBy: "date",
                descending: true,
                page: 1,
                rowsPerPage: 25,
            },
            columns: [
                {
                    name: "date",
                    align: "left",
                    label: "Date",
                    field: "date",
                    sortable: true,
                },
                {
                    name: "type",
                    align: "left",
                    label: "Type",
                    field: "type",
                    sortable: true,
                },
                {
                    name: "item",
                    align: "left",
                    label: "Objet",
                    field: "item",
                    sortable: true,
                    style: 'max-width: 400px; width: 300px'
                },
                {
                    name: "actions",
                    align: "center",
                    label: "",
                    field: "",
                    sortable: false,
                },
            ],
        }
    },
    watch: {
        filter: {
            handler(newValue, oldValue) {
                // console.log(`${this.$options.name} | filter()`)
                this.query()
            },
            deep: true
        },
    },
    async created() {

        this.query()

    },
    methods: {
        // downloadICS,
        async onRequest(props) {

            // update pagination object
            this.pagination = props.pagination
            this.pagination.rowsPerPage = props.pagination.rowsPerPage === 0 ? this.pagination.rowsNumber : props.pagination.rowsPerPage

            // update table rows
            this.query()
        },
        async query() {

            this.loading = true
            // if (this.filter.search.length >= 3) {
            this.data = await store.getEvents(this.filter, this.pagination.page, this.pagination.rowsPerPage, this.pagination.sortBy, this.pagination.descending)
            this.rows = this.data.results
            this.pagination.rowsNumber = this.data.nrows
            this.loading = false
        },
        handleDeletion(val) {
            this.selected = val
            this.dialog.deletion = true
        },
        reset() {
            this.filter.search = ""
        },
        async remove() {

            // console.log(`delete ${this.selected}`)
            let message = await store.deleteEvent(this.selected)
            if (message) {
                this.query()
            }
        }
    }
}
</script>
<style scoped></style>