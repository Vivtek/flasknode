<template>
 <v-layout row wrap>
  <v-flex xs8 offset-md2>
   <MessagePostForm />
   <div v-for="message in messages" :key="message.id">
    <v-card raised>
     <v-card-title>Message #{{ message.id }}</v-card-title>
     <v-card-text>{{ message.message }}</v-card-text>
    </v-card>
    <v-spacer></v-spacer>
   </div>
  </v-flex>
 </v-layout>
</template>

<script>
import MessagePostForm from './MessagePostForm'
import axios from 'axios'

export default {
  name: 'MessageFeed',

  data: () => ({
    messages: null
  }),
  components: {
    MessagePostForm,
  },
  mounted () {
    axios
       .get('http://localhost:5000/message/list')
       .then(response => (this.messages = response.data))

  }
};
</script>
