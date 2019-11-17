<template>
 <v-card>
   <v-form
     ref="form"
   >
     <v-textarea placeholder="What are you thinking today?"
      v-model="message"
     ></v-textarea>
     <v-btn
      color="success"
      class="mr-4"
      @click="post"
     >
      POST
     </v-btn>
   </v-form>
 </v-card>
</template>

<script>
import axios from 'axios'

export default {
  name: 'MessagePostForm',

  data: () => ({
    message: null
  }),
  methods: {
    post () {
       if (this.message != null) {
          axios
             .post('http://localhost:5000/message/post',
                {
                   message: this.message,
                }
             )
          this.message = null
       }
    }
  }
};
</script>
