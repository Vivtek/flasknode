<template>
 <v-card>
   <v-form
     ref="form"
   >
     <v-text-field
      v-model="message"
     ></v-text-field>
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
       axios
          .post('http://localhost:5000/message/post',
             {
                message: this.message,
             }
          )
    }
  }
};
</script>
