<template>
    <Form :model="document" :edit="edit" :changewatch="changewatch">

        <template v-slot:body>

            <!-- FILE SECTION -->
            <FormSection title="" class="q-mt-none">
                <template v-slot:content>

                    <!-- FILE SELECTOR FIELD -->
                    <div class="col q-my-md" v-if="!document.file">
                        <!-- counter max-files="1" -->
                        <q-file bg-color="white" outlined v-model="newFile" label="Sélectionner un fichier" :rules="[v => checkFile(v)]" clearable @update:model-value="getFileAttributes">
                            <template v-slot:prepend>
                                <q-icon name="sym_o_attach_file" />
                            </template>
                        </q-file>
                    </div>

                    <!-- ATTACHED FILE CARD -->
                    <q-card class="col q-my-md" flat bordered v-if="document.file">

                        <q-item>
                            <q-item-section avatar>
                                <!-- <q-avatar color="none" text-color="black" icon="sym_o_file_present" /> -->
                                <q-icon name="sym_o_file_present" color="grey-8" size="30px" class="q-ma-none" />
                            </q-item-section>

                            <q-item-section>
                                <q-item-label><a :href="fileDownloadUrl">{{ document.filename }}</a></q-item-label>
                                <q-item-label caption>{{ formatBytes(document.size) }}</q-item-label>
                            </q-item-section>

                            <q-item-section avatar>
                                <q-btn dense round flat color="red" name="delete" @click="showDeleteDialog(document)" icon="sym_o_delete" :disable="!edit">
                                    <q-tooltip class="bg-black">Supprimer</q-tooltip>
                                </q-btn>
                            </q-item-section>
                        </q-item>

                    </q-card>


                    <div class="row q-col-gutter-lg q-py-md">

                        <!-- REFERENCE TEXT FIELD -->
                        <div class="col-xs-12 col-sm-12 col-md-6 col-lg-6">
                            <q-input bg-color="white" outlined v-model="document.reference" label="N° référence" :disable="!edit" />
                        </div>

                        <!-- TITLE TEXT FIELD -->
                        <div class="col-xs-12 col-sm-12 col-md-6 col-lg-6">
                            <q-input bg-color="white" outlined v-model="document.title" label="Titre" :rules="[v => checkFilled(v)]" :disable="!edit" />
                        </div>

                    </div>

                    <div class="row q-col-gutter-lg q-py-md">

                        <!-- TYPE SELECT FIELD -->
                        <div class="col-xs-12 col-sm-12 col-md-6 col-lg-6">
                            <!-- v-model="entity.type" :options="entityTypes" option-label="name" option-value="id" emit-value map-options label="Type"  -->
                            <q-select bg-color="white" outlined v-model="document.type" :options="documentTypes" option-label="name" option-value="id" emit-value map-options label="Type" :rules="[v => checkFilled(v)]" clearable :disable="!edit">
                                <template v-slot:option="scope">
                                    <q-item v-bind="scope.itemProps">
                                        <q-item-section>
                                            <q-item-label>{{ scope.opt.name }}</q-item-label>
                                        </q-item-section>
                                    </q-item>
                                </template>
                            </q-select>
                        </div>

                    </div>

                    <!-- NOTE TEXT AREA FIELD -->
                    <div class="row q-col-gutter-lg  q-py-md">
                        <div class="col">
                            <q-input bg-color="white" outlined v-model="document.note" label="Notes" type="textarea" :disable="!edit" counter maxlength="500" />
                        </div>
                    </div>


                    <!-- SEARCH ITEMS FIELD -->
                    <!-- @update:model-value="query()"-->
                    <!-- 
                    <div class="row q-col-gutter-lg  q-py-sm">

                        <div class="col">
                            <q-input class="q-pa-none q-ma-none" bg-color="white" v-model="filter.search" outlined placeholder="Rechercher un objet (n° ou titre)"> 
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

                    </div>
                    -->

                    <!-- SEARCH ITEMS FIELD -->
                    <div class="row q-col-gutter-lg  q-py-sm">

                        <div class="col">
                            <!-- <q-select bg-color="white" outlined v-model="myitem" use-input hide-selected :options="itemOptions" option-label="title" option-value="id" emit-value map-options @update:model-value="selectOption" @filter="filterFn" label="Lier des objets parlementaires à ce document" :disable="!edit || !store.user.is_manager"> -->
                            <q-select bg-color="white" outlined v-model="myitem" use-input hide-selected :options="itemOptions" option-label="title" @update:model-value="selectOption" @filter="filterFn" label="Lier des objets parlementaires à ce document" :disable="!edit || !store.user.is_manager">
                                <template v-slot:prepend>
                                    <q-icon name="sym_o_search" />
                                </template>

                                <template v-slot:option="scope">

                                    <q-item v-bind="scope.itemProps">
                                        <q-item-section side>
                                            <q-icon outline dense round color="blue" name="sym_o_add" />
                                        </q-item-section>

                                        <q-item-section>
                                            <q-item-label>{{ scope.opt.number }} - {{ scope.opt.title }}</q-item-label>
                                            <!-- <q-item-label caption>{{ scope.opt.type }}</q-item-label> -->
                                        </q-item-section>
                                        <!--
                                        <q-item-section side>
                                            <q-chip dense square :color="scope.opt.active ? 'green' : 'red'" text-color="white">
                                                {{ scope.opt.active ? 'ACTIF' : 'INACTIF' }}
                                            </q-chip>
                                        </q-item-section>
                                        -->
                                    </q-item>
                                </template>

                                <!--
                                <template v-slot:append>
                                    <q-spinner color="blue-grey" :thickness="3" v-if="loading.items" />
                                </template>
                                -->

                                <!-- 
                                <template v-slot:after>
                                    <q-btn round unelevated color="blue-grey-8" icon="sym_o_person_add" @click="addEntity()" :disable="!edit || !store.user.is_manager">
                                        <q-tooltip class="bg-black">Ajouter une nouvelle option</q-tooltip>
                                    </q-btn>
                                </template>
                                -->

                            </q-select>
                        </div>

                    </div>



                    <!-- AUTHOR SELECT/CREATE FIELD -->
                    <!--
                    <div class="col-xs-12 col-sm-12 col-md-6 col-lg-6">

                        <q-select bg-color="white" outlined v-model="item.author" use-input :options="authorOptions" option-label="name" option-value="id" emit-value map-options @filter="filterFn" label="Auteur" clearable :rules="[v => checkFilled(v)]" :disable="!edit || !store.user.is_manager">

                            <template v-slot:prepend>
                                <q-icon name="sym_o_search" />
                            </template>

                            <template v-slot:option="scope">
                                <q-item v-bind="scope.itemProps">
                                    <q-item-section>
                                        <q-item-label>{{ scope.opt.name }}</q-item-label>
                                        <q-item-label caption>{{ scope.opt.type }}</q-item-label>
                                    </q-item-section>
                                    <q-item-section side>
                                        <q-chip dense square :color="scope.opt.active ? 'green' : 'red'" text-color="white">
                                            {{ scope.opt.active ? 'ACTIF' : 'INACTIF' }}
                                        </q-chip>
                                    </q-item-section>
                                </q-item>
                            </template>

                            <template v-slot:append>
                                <q-spinner color="blue-grey" :thickness="3" v-if="loading.authors" />
                            </template>

                            <template v-slot:after>
                                <q-btn round unelevated color="blue-grey-8" icon="sym_o_person_add" @click="addEntity()" :disable="!edit || !store.user.is_manager">
                                    <q-tooltip class="bg-black">Ajouter une nouvelle option</q-tooltip>
                                </q-btn>
                            </template>

                        </q-select>

                    </div>
                    -->


                    <!-- LINKED ITEMS -->
                    <div class="row q-col-gutter-lg">
                        <div class="col">
                            <q-list dense class="rounded-borders">

                                <!-- <q-item class="rounded-borders bg-white text-white" v-for="item in document.items"> -->
                                <div v-for="item in document.items">

                                    <q-item>
                                        <q-item-section avatar class="items-center q-mx-none q-px-none q-py-none q-my-none">
                                            <q-badge :color="item.status.color" rounded />
                                            <q-tooltip class="bg-black">{{ item.status.name }}</q-tooltip>
                                        </q-item-section>

                                        <q-item-section>

                                            <!--<q-chip clickable square outline color="blue-5" text-color="white" icon="sym_o_loupe"> -->
                                            <div class="ellipsis"> <router-link :to="{
                                                name: 'Item',
                                                params: {
                                                    id: item.id
                                                }
                                            }">{{ item.number }} - {{ item.title }} </router-link></div>
                                            <!-- </q-chip> -->

                                        </q-item-section>

                                        <q-item-section avatar>
                                            <q-btn outline dense round color="red" name="unlink" @click="handleUnlink(item.uuid)" icon="sym_o_remove" :disable="!edit">
                                                <q-tooltip class="bg-black">Déconnecter cet objet parlementaire du document</q-tooltip>
                                            </q-btn>
                                        </q-item-section>

                                    </q-item>
                                    <q-separator inset />
                                </div>

                            </q-list>
                        </div>
                    </div>

                    <!-- TODO REMOVE/DEV DISPLAY JSON-->
                    <div class="bg-light-blue-1 q-my-md q-pa-md" v-if="store.dev">
                        <div>document</div>
                        <div>{{ document }}</div>
                    </div>

                </template>
            </FormSection>

        </template>

    </Form>

    <!-- DELETE DIALOG -->
    <DeleteDialog v-model="dialog.deletion" @delete-event="handleDelete" :content="dialog_content" />

</template>

<script>
import { store } from '../store/store.js'
import { checkFilled, checkFile, formatBytes } from '../store/shared.js'
import Form from "../components/Form.vue"
import FormSection from "../components/FormSection.vue"
import DeleteDialog from './DeleteDialog.vue'

export default {
    name: 'DocumentForm',
    components: { Form, FormSection, DeleteDialog },
    props: { 'item_type': Number, 'edit': Boolean, 'modelValue': Object, 'changewatch': { type: Boolean, default: true } },
    emits: ['update:modelValue'],
    setup() {
        return {
        }
    },
    data() {
        return {
            store,
            myitem: [],
            filter: { search: "" },
            dialog: { deletion: false },
            dialog_content: undefined,
            documentTypes: [],
            itemOptions: [],
            newFile: null,
            valid: null,
        }
    },
    computed: {
        document: {
            get() {
                return this.modelValue
            },
            set(document) {
                this.$emit('update:modelValue', document)
            }
        },
        fileDownloadUrl() {
            return `${this.store.host}/api/document/${this.document.uuid}/download/`;
        }

    },
    async created() {
        this.documentTypes = await this.store.getDocumentTypes()
        // getItems(filter = {}, page = 1, size = 10, sortBy = "", descending = "false") 
        this.itemOptions = (await store.getItems({ search: "" }, 1, 5, "number", "false")).results
        // this.getDocumentTypes()
    },
    methods: {
        formatBytes,
        checkFilled,
        checkFile,
        validation(val) {
            // console.log(`${this.$options.name} | validation: ${val}`)
            this.valid = val
            // this.$emit('validationEvent', this.valid)
        },
        filterFn(val, update, abort) {

            /*
            this.loading = true
            this.data = await store.getItems(this.filter, this.pagination.page, this.pagination.rowsPerPage, this.pagination.sortBy, this.pagination.descending)
            this.rows = this.data.results
            this.pagination.rowsNumber = this.data.nrows
            this.loading = false
            */

            update(async () => {
                // this.loading.authors = true
                const str = val.toLowerCase()
                // getItems(filter = {}, page = 1, size = 10, sortBy = "", descending = "false") 
                this.itemOptions = (await store.getItems({ search: str }, 1, 5, "number", "false")).results
                // this.loading.authors = false
            })
        },
        selectOption(payload) {

            console.log("select Option")
            console.log(payload)
            console.log("myitem")
            console.log(this.myitem)

            const exists = this.document.items.some(item => item.uuid === payload.uuid);
            if (!exists) {
                this.document.items.push(payload)
            }

        },
        getFileAttributes() {
            console.log("getFileAttributes()")
            if (this.newFile) {
                console.log("this.newFile exists")
                this.document.file = this.newFile
                this.document.filename = this.newFile.name
                this.document.size = this.newFile.size
            }
        },
        showDeleteDialog(val) {
            this.dialog_content = `Supprimer définitivement le document '${val.filename}' ?`
            this.dialog.deletion = true
        },
        handleDelete() {
            this.document.file = null
            this.newFile = null
        },
        handleUnlink(uuid) {

            this.document.items = this.document.items.filter(item => item.uuid !== uuid);
        }
    }
}
</script>

<style scoped></style>