<template>
    <div class="shadow sm:overflow-hidden sm:rounded-md max-w-lg">
      <Form @submit="submit" :validation-schema="schema">
        <div class="space-y-6 bg-white py-6 px-4 sm:p-6">
          <div>
            <h3 class="text-lg font-medium leading-6 text-gray-900">{{  title }}</h3>
            <p class="mt-1 text-sm text-gray-500">{{  description }}</p>
          </div>

          <div class="space-y-1">
            <label for="original" class="block text-sm font-medium text-gray-700">Original password</label>
            <div class="mt-1 group relative inline-block w-full">
              <Field id="original" name="original" type="password" autocomplete="password" class="block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 placeholder-gray-400 shadow-sm focus:border-rose-600 focus:outline-none focus:ring-rose-600 sm:text-sm" />
              <ErrorMessage name="original" class="absolute left-5 top-5 translate-y-full w-48 px-2 py-1 bg-gray-700 rounded-lg text-center text-white text-sm after:content-[''] after:absolute after:left-1/2 after:bottom-[100%] after:-translate-x-1/2 after:border-8 after:border-x-transparent after:border-t-transparent after:border-b-gray-700"/>
            </div>
          </div>

          <div class="space-y-1">
            <label for="full_name" class="block text-sm font-medium text-gray-700">Your name</label>
            <div class="mt-1 group relative inline-block w-full">
              <Field 
                id="full_name" 
                name="full_name" 
                type="string"
                v-model="profile.full_name"
                class="mt-1 block w-full rounded-md border border-gray-300 py-2 px-3 shadow-sm focus:border-rose-500 focus:outline-none focus:ring-rose-500 sm:text-sm" 
              />
              <ErrorMessage name="email" class="absolute left-5 top-5 translate-y-full w-48 px-2 py-1 bg-gray-700 rounded-lg text-center text-white text-sm after:content-[''] after:absolute after:left-1/2 after:bottom-[100%] after:-translate-x-1/2 after:border-8 after:border-x-transparent after:border-t-transparent after:border-b-gray-700"/>
            </div>
          </div>

          <div class="space-y-1">
            <label for="email" class="block text-sm font-medium text-gray-700">Email address</label>
            <div class="mt-1 group relative inline-block w-full">
              <Field 
                id="email" 
                name="email" 
                type="email" 
                autocomplete="email" 
                v-model="profile.email"
                class="block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 placeholder-gray-400 shadow-sm focus:border-rose-600 focus:outline-none focus:ring-rose-600 sm:text-sm" 
              />
              <ErrorMessage name="email" class="absolute left-5 top-5 translate-y-full w-48 px-2 py-1 bg-gray-700 rounded-lg text-center text-white text-sm after:content-[''] after:absolute after:left-1/2 after:bottom-[100%] after:-translate-x-1/2 after:border-8 after:border-x-transparent after:border-t-transparent after:border-b-gray-700"/>
            </div>
          </div>
        </div>
        <div class="py-3 pb-6 text-right sm:px-6">
          <button type="submit" class="inline-flex justify-center rounded-md border border-transparent bg-rose-500 py-2 px-4 text-sm font-medium text-white shadow-sm hover:bg-rose-700 focus:outline-none focus:ring-2 focus:ring-rose-600 focus:ring-offset-2">
            Submit
          </button>
        </div>
      </Form>
    </div>
</template>

<script setup lang="ts">
import { useAuthStore } from "@/stores"
import { IUserProfileUpdate } from "@/interfaces"

const auth = useAuthStore()
let profile = {} as IUserProfileUpdate
const title = "Personal settings"
const description = "Changing your email address will change your login. Any changes will require you to enter your original password."

const schema = {
    original: { required: auth.profile.password, min: 8, max: 64 },
    full_name: { required: false },
    email: { email: true, required: true },
}

onMounted( () => {
  resetProfile()
})

function resetProfile() {
  profile = {
    full_name: auth.profile.full_name,
    email: auth.profile.email,
  }
}

async function submit(values: any) {
  profile = {}
  if ((!auth.profile.password && !values.original) || 
      (auth.profile.password && values.original)) {
    if (values.original) profile.original = values.original
    if (values.email) {
      profile.email = values.email
      if (values.full_name) profile.full_name = values.full_name
      await auth.updateUserProfile(profile)
      resetProfile()
    }
  }
}
</script>