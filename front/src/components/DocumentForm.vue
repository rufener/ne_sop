<template>
    <Form :model="document" :edit="edit" :changewatch="changewatch">

        <template v-slot:body>

            <!-- FILE SECTION -->
            <FormSection title="" class="q-mt-none">
                <template v-slot:content>

                    <!-- FILE SELECTOR FIELD -->
                    <div class="col q-my-md" v-if="!document.filename">
                        <q-file bg-color="white" outlined v-model="newFile" label="Sélectionner un fichier" :rules="[v => checkFile(v)]" @update:model-value="getFileAttributes">
                            <template v-slot:prepend>
                                <q-icon name="sym_o_attach_file" />
                            </template>
                        </q-file>
                    </div>

                    <!-- ATTACHED FILE CARD -->
                    <q-card class="col q-my-md" flat bordered v-if="document.filename">

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
                                <q-btn dense round flat color="red" name="delete" @click="showFilepicker()" icon="sym_o_delete" :disable="!edit">
                                    <!-- <q-btn dense round flat color="red" name="delete" @click="showDeleteDialog(document)" icon="sym_o_delete" :disable="!edit">-->
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
                            <!-- option-value="id" emit-value map-options -->
                            <q-select bg-color="white" outlined v-model="document.type" :options="documentTypes" option-label="name" label="Type" :rules="[v => checkFilled(v)]" clearable :disable="!edit">
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
                    <div class="row q-col-gutter-lg q-py-md">
                        <div class="col">
                            <q-input bg-color="white" outlined v-model="document.note" label="Notes" type="textarea" :disable="!edit" counter maxlength="500" />
                        </div>
                    </div>

                    <!-- SEARCH ITEMS FIELD -->
                    <div class="row q-col-gutter-lg q-py-sm" v-if="!excludeFields.includes('search-items')">

                        <div class="col">

                            <q-select bg-color="white" outlined v-model="myitem" use-input hide-selected :options="itemOptions" option-label="title" @update:model-value="selectOption" @filter="filterFn" label="Lier des objets parlementaires à ce document" :disable="!edit || !store.user.is_manager">
                                <template v-slot:prepend>
                                    <q-icon name="sym_o_search" />
                                </template>

                                <template v-slot:option="scope">

                                    <q-item v-bind="scope.itemProps">
                                        <q-item-section side>
                                            <q-icon outline dense round color="blue" name="sym_o_add" v-if="!scope.opt.disable" />
                                            <q-icon outline dense round color="red" name="sym_o_block" v-if="scope.opt.disable" />
                                        </q-item-section>

                                        <q-item-section>
                                            <q-item-label>{{ scope.opt.number }} - {{ scope.opt.title }}</q-item-label>
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


                            </q-select>
                        </div>

                    </div>

                    <!-- LINKED ITEMS -->
                    <div class="row q-col-gutter-lg" v-if="!excludeFields.includes('search-items')">
                        <div class="col">
                            <q-list dense class="rounded-borders">

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
    <!-- 
    <DeleteDialog v-model="dialog.deletion" @delete-event="handleDelete" :content="dialog_content" />
    -->

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
    props: { 'item_type': Number, 'edit': Boolean, 'modelValue': Object, 'changewatch': { type: Boolean, default: true }, 'excludeFields': { type: Array, default: () => [] } },
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
        this.getItemOptions()
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
        checkFilename(val) {
            console.log(val)
        },
        async getItemOptions(searchstring = "") {

            const options = (await store.getItems({ search: searchstring.toLowerCase() }, 1, 5, "number", "false")).results
            options.map(x => x.disable = this.document.items.some(item => item.uuid === x.uuid))
            this.itemOptions = options

        },
        filterFn(val, update, abort) {
            update(async () => {
                this.getItemOptions(val)
            })
        },
        selectOption(payload) {

            console.log("select Option")
            console.log(payload)
            console.log("myitem")
            console.log(this.myitem)

            // Check if item has already been added to list
            const exists = this.document.items.some(item => item.uuid === payload.uuid);
            if (!exists) {
                this.document.items.push(payload)
            }

        },
        getFileAttributes() {
            console.log("getFileAttributes()")
            console.log(this.newFile)
            if (this.newFile) {
                console.log("this.newFile exists")
                this.document.file = this.newFile
                this.document.filename = this.newFile.name
                this.document.size = this.newFile.size
            }
        },
        showFilepicker() {
            this.newFile = null // new File([], "", { type: "text/plain" });
            this.document.file = null
            this.document.filename = null
            this.document.size = null
        },
        handleUnlink(uuid) {
            this.document.items = this.document.items.filter(item => item.uuid !== uuid);
        }
    }
}
</script>

<style scoped></style>