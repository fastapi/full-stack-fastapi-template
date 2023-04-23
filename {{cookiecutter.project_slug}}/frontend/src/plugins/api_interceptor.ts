import Vue from 'vue';
import axios from 'axios';

const NotAllowedPlugin = {
  install(Vue, options) {axios.interceptors.response.use(
      (response) => {
        return response;
      },
      (error) => {
        if (error.response) {
          if (error.response.status === 401) {
            console.log('Unauthorized request');
          }
          return Promise.reject(error);
        }
      }
    );
  }
};

Vue.use(NotAllowedPlugin)
