<template>
 <v-card>
 Test.
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
  mounted: () => {
    axios
       .get('http://localhost:5000/message/list')
       .then(response => (this.info = response))
       .catch(error => { console.log(error) })
  }
};
</script>
