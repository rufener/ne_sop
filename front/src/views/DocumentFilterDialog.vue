<template>
    <q-dialog v-model="showModel">
        <q-card style="width: 700px; max-width: 80vw;">
            <q-card-section class="bg-blue-grey text-white">
                <div class="text-h6">Filtres</div>
            </q-card-section>

            <q-card-section class="items-center scroll" style="max-height: 70vh">

                <div class="row q-col-gutter-lg q-py-md">

                    <!-- DOCUMENT TYPE -->
                    <div class="col-xs-12 col-sm-12 col-md-12 col-lg-12">
                        <q-select bg-color="white" outlined v-model="filter.type" :options="documentTypes" option-label="name" option-value="id" emit-value map-options label="Type(s)" multiple @update:model-value="" @clear="clear('type')">

                            <template v-slot:option="scope">
                                <q-item v-bind="scope.itemProps">

                                    <q-item-section side>
                                        <q-checkbox :model-value="scope.selected" @update:model-value="scope.toggleOption(scope.opt)" />
                                    </q-item-section>
                                    <q-item-section>
                                        <q-item-label>{{ scope.opt.name }}</q-item-label>
                                    </q-item-section>

                                </q-item>
                            </template>

                            <template v-slot:before-options="props">
                                <q-item>
                                    <q-item-section>
                                        <div class="row">
                                            <q-btn @click="filter.type = documentTypes.map(x => x.id)" label="Toutes les options" dense class="col q-ma-sm"></q-btn>
                                            <q-btn @click="filter.type = []" label="Aucune option" dense class="col q-ma-sm"></q-btn>
                                        </div>
                                    </q-item-section>
                                </q-item>
                            </template>

                            <template v-slot:append>
                                <q-spinner color="blue-grey" :thickness="3" v-if="loading" />
                            </template>

                        </q-select>
                    </div>

                </div>

            </q-card-section>

            <q-card-actions align="right">
                <q-btn flat label="Réinitialiser" color="primary" @click="resetall()" />
                <q-btn flat label="Fermer" color="primary" v-close-popup />
            </q-card-actions>
        </q-card>
    </q-dialog>
</template>

<script>
import { store } from '../store/store.js'

export default {
    name: 'DocumentFilterDialog',
    components: {},
    props: { 'filter': Object, 'show': { type: Boolean, default: false } },
    emits: ['update:modelValue', 'update:show'],
    data() {
        return {
            store,
            loading: true,
            documentTypes: [],
            dialog: true,
        }
    },
    computed: {
        filterModel: {
            get() {
                return this.filter
            },
            set(filterModel) {
                this.$emit('update:filter', filterModel)
            }
        },
        showModel: {
            get() {
                return this.show
            },
            set(showModel) {
                this.$emit('update:show', showModel)
            }
        },
    },
    methods: {
        clear(val) {
            // console.log(`${this.$options.name} | reset()`)
            // console.log(val)
            this.filterModel[val] = []
        },
        resetall() {
            this.filterModel.search = ''
            this.filterModel.type = this.documentTypes.map(x => x.id)
        }
    },
    async created() {
        // console.log(`${this.$options.name} | created`)
        this.documentTypes = await store.getDocumentTypes()
        this.loading = false
    }
}
</script>

<style scoped></style>