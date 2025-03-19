<template>
  <!-- DELETE DIALOG -->
  <q-dialog :model-value="modelValue" @hide="close()">
    <q-card>

      <q-bar class="bg-red">
        <q-space />
        <q-btn dense flat icon="close" v-close-popup>
          <q-tooltip class="bg-white text-primary">Annuler</q-tooltip>
        </q-btn>
      </q-bar>

      <q-card-section>
        <div class="text-h6" color="red"><q-icon name="warning" color="warning" size="3rem" /> {{ title }}</div>
      </q-card-section>

      <q-card-section class="row items-center">
        <span class="text-body1">{{ content }}</span>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="Annuler" color="primary" v-close-popup />
        <q-btn flat label="Supprimer" color="red" @click="remove" v-close-popup />
      </q-card-actions>

    </q-card>
  </q-dialog>
</template>

<script>
export default {
  name: 'DeleteDialog',
  props: {
    'modelValue': Boolean,
    'content': { type: String, default: () => 'Supprimer définitivement cette entrée et tous les éléments liés?' },
    'title': { type: String, default: () => 'Suppression' }
  },
  emits: ['update:modelValue', 'deleteEvent'],
  methods: {
    remove() {
      this.$emit('deleteEvent')
    },
    close() {
      this.$emit('update:modelValue', false)
    }
  }
}
</script>
