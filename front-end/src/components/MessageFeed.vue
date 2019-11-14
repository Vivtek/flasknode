<template>
 <v-card>
 {{ info }}
 </v-card>
</template>

<script>
import axios from 'axios'

export default {
  name: 'MessageFeed',

  data: () => ({
    info: null
  }),
  mounted () {
    axios
       .get('http://localhost:5000/message/list')
       .then(response => (this.info = response.data))

  }
};
</script>
