<template>
 <v-layout row wrap>
  <v-flex xs8 offset-md2>
   <MessagePostForm />
   <div>
    <v-alert :color="alert" v-if="alert">
      {{ alert_message }}
    </v-alert>
   </div>
   <div v-for="message in messages" :key="message.id">
    <v-card raised>
     <v-card-title>Posted {{ message.date | ago }} [{{ message.id }}]</v-card-title>
     <v-card-subtitle> {{ message.date | prettier_date }}</v-card-subtitle>
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
import moment from 'moment'

export default {
  name: 'MessageFeed',

  data: () => ({
    messages: null,
    alert: null,
    alert_message: 'Alert!'
  }),
  components: {
    MessagePostForm,
  },
  filters: {
    pretty_date: function (date) {
       return moment(date).format('dddd, LL [at] h:mm a')
    },
    prettier_date: function (date) {
       return moment(date).calendar(null, { sameElse: 'LL [at] h:mm a' })
    },
    ago: function (date) {
       return moment(date).fromNow()
    }
  },
  sockets: {
    connect: function () {},
    feed: function (data) {
       this.messages.unshift (data)
    }
  },
  methods: {
     do_alert (message) {
        this.alert_message = message
        this.alert='info'
        let timer = this.do_alert.timer
        if (timer) {
           clearTimeout(timer)
        }
        this.do_alert.timer = setTimeout(() => {
           this.alert=null
        }, 3000)
     }
  },
  mounted () {
    axios
       .get('http://localhost:5000/message/list')
       .then(response => (this.messages = response.data))
  },
  created () {
    //this.sockets.subscribe ('FEED', (data) => {
    //   this.messages.push (data)
    //})
    this.$socket.emit('join', {topic:'feed'})
  }
};
</script>
