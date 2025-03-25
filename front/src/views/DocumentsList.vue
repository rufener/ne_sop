<template>
    <div class="q-pa-sm q-gutter-sm">

        <!-- BREADCRUMBS NAVIGATION -->
        <q-breadcrumbs style="font-size: 16px">
            <q-breadcrumbs-el label="Documents" to="/documents" />
        </q-breadcrumbs>

        <!-- SEARCH AND FILTER SECTION -->
        <div class="row q-col-gutter-md q-px-sm q-mt-xs items-center">

            <!-- SEARCH RECORDS FIELD -->
            <div class="col-xs-12 col-sm-8 col-md-6 col-lg-6">
                <q-input bg-color="white" v-model="filter.search" outlined dense placeholder="Rechercher (réf., titre, objet lié)"> <!-- @update:model-value="query()" -->
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
            <div class="col-xs-12 col-sm-4 col-md-6 col-lg-6">
                <q-btn padding="sm md" unelevated no-caps color="blue-grey-8" text-color="white" icon="sym_o_add_circle" label="Ajouter" class="q-py-none q-my-none" @click="" to="/documents/new">
                    <q-tooltip class="bg-black">Ajouter un nouveau document</q-tooltip>
                </q-btn>
            </div>


        </div>

        <!-- DOCUMENTS TABLE -->
        <q-table title="" :rows="rows" :columns="columns" row-key="id" v-model:pagination="pagination" :loading="loading" @request="onRequest" binary-state-sort class="q-my-lg">
            <!-- TABLE BODY -->
            <template v-slot:body="props">
                <q-tr :props="props">

                    <!-- TITLE COLUMN -->
                    <q-td key="title" :props="props" style="max-width: 250px">
                        <router-link :to="{
                            name: 'Document',
                            params: {
                                id: props.row.uuid
                            }
                        }">

                            <!-- icon="sym_o_loupe" -->
                            <q-chip clickable square outline color="blue-5" text-color="white" class="q-mx-none">
                                <div class="ellipsis"><b>{{ props.row.title }}</b> / {{ props.row.reference }}</div>
                            </q-chip>
                        </router-link>
                    </q-td>

                    <!-- TYPE COLUMN -->
                    <q-td key="type" :props="props">
                        {{ props.row.type }}
                    </q-td>

                    <!-- ITEMS COLUMN -->
                    <q-td key="type" :props="props">
                        <div v-for="item in props.row.items" style="max-width: 280px">
                            <router-link :to="{
                                name: 'Item',
                                params: {
                                    id: item.uuid
                                }
                            }">
                                <!-- icon="sym_o_loupe" -->
                                <!--
                                                                    <q-item-section avatar class="items-center q-mx-none q-px-none q-py-none q-my-none">
                                            <q-badge :color="item.status.color" rounded />
                                            <q-tooltip class="bg-black">{{ item.status.name }}</q-tooltip>
                                        </q-item-section>
                             -->
                                <q-chip clickable square outline color="blue-5" text-color="white" class="q-mx-none">
                                    <div class="vertical-middle ellipsis"><q-badge :color="item.status.color" rounded class="q-mr-xs" /> <b>{{ item.number }}</b> - {{ item.title }}</div>

                                    <q-tooltip class="bg-black text-white text-body2 q-pa-none q-ma-none">
                                        <q-card class="bg-black text-white">

                                            <q-card-section>
                                                <div class="bg-white text-black text-subtitle2 text-weight-bolder q-pa-xs">{{ item.number }} - {{ item.type.name }}</div>
                                                <div class="text-subtitle2">{{ item.title }}</div>
                                                <div class="text-subtitle2">Auteur: {{ item.author.name }}</div>
                                                <div class="text-subtitle2">Service: {{ item.lead.name }}</div>
                                            </q-card-section>
                                            <q-card-section>
                                                <div class=""><q-badge :color="item.status.color" rounded class="q-mr-xs" /> {{ item.status.name }}</div>
                                            </q-card-section>
                                        </q-card>
                                    </q-tooltip>
                                </q-chip>
                            </router-link>
                        </div>
                    </q-td>

                    <!-- DATE COLUMN -->
                    <q-td key="modified" :props="props">
                        {{ props.row.modified }}
                    </q-td>

                    <!-- USER COLUMN -->
                    <q-td key="author" :props="props">
                        {{ props.row.author }}
                    </q-td>

                    <!-- ACTIONS COLUMN -->
                    <q-td key="actions" :props="props">
                        <div class="float-right">
                            <q-btn dense round flat color="grey" name="download" @click="" :href="`${store.host}/api/document/${props.row.uuid}/download/`" icon="sym_o_download">
                                <q-tooltip class="bg-black">Télécharger {{ props.row.filename }}</q-tooltip>
                            </q-btn>
                            <q-btn dense round flat color="red" name="delete" @click="handleDeletion(props.row.uuid)" icon="sym_o_delete">
                                <q-tooltip class="bg-black">Supprimer</q-tooltip>
                            </q-btn>
                        </div>
                    </q-td>
                </q-tr>
            </template>
            <template v-slot:no-data>
                Aucune fichier
            </template>
        </q-table>

        <!-- TODO REMOVE/DEV DISPLAY JSON-->
        <div class="bg-light-blue-1 q-my-md q-pa-md" v-if="store.dev">
            <div>store.documents</div>
            <div>{{ rows }}</div>
        </div>

        <!-- DELETE DIALOG -->
        <DeleteDialog v-model="dialog.deletion" @delete-event="remove" content="Supprimer définitivement ce document? Les objets parlementaires liés ne seront pas supprimés." title="Suppression définitive du document" />

    </div>
</template>

<script>
import { store } from '../store/store.js'
import DeleteDialog from '../components/DeleteDialog.vue'

export default {
    name: 'DocumentsList',
    components: { DeleteDialog },
    props: { 'title': String },
    emits: [],
    data() {
        return {
            store,
            selected: null,
            filter: { search: "" },
            dialog: { deletion: false },
            data: null,
            rows: [],
            loading: false,
            pagination: {
                rowsNumber: 0,
                sortBy: "id",
                descending: true,
                page: 1,
                rowsPerPage: 25,
            },
            columns: [
                {
                    name: "title",
                    align: "left",
                    label: "Titre / Réf.",
                    field: "title",
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
                    name: "items",
                    align: "left",
                    label: "Objet(s) lié(s)",
                    field: "items",
                    sortable: false,
                },
                {
                    name: "modified",
                    align: "left",
                    label: "Modifié le",
                    field: "modified",
                    sortable: true,
                },
                {
                    name: "author",
                    align: "left",
                    label: "Utilisateur",
                    field: "author",
                    sortable: true,
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
            this.data = await store.getDocuments(this.filter, this.pagination.page, this.pagination.rowsPerPage, this.pagination.sortBy, this.pagination.descending)
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
            let message = await store.deleteDocument(this.selected)
            if (message) {
                this.query()
            }
        }
    }
}
</script>
<style scoped></style>