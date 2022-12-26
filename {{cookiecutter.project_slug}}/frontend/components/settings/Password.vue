<template>
  <div class="shadow sm:overflow-hidden sm:rounded-md min-w-max">
    <Form @submit="submit" :validation-schema="schema">
      <div class="space-y-6 bg-white py-6 px-4 sm:p-6">
        <div>
          <h3 class="text-lg font-medium leading-6 text-gray-900">{{  title }}</h3>
          <p class="mt-1 text-sm text-gray-500">{{  description }}</p>
        </div>

        <div class="space-y-1">
          <label for="password" class="block text-sm font-medium text-gray-700">Password</label>
          <div class="mt-1 group relative inline-block w-full">
            <Field id="password" name="password" type="password" autocomplete="password" class="block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 placeholder-gray-400 shadow-sm focus:border-rose-600 focus:outline-none focus:ring-rose-600 sm:text-sm" />
            <ErrorMessage name="password" class="absolute left-5 top-5 translate-y-full w-48 px-2 py-1 bg-gray-700 rounded-lg text-center text-white text-sm after:content-[''] after:absolute after:left-1/2 after:bottom-[100%] after:-translate-x-1/2 after:border-8 after:border-x-transparent after:border-t-transparent after:border-b-gray-700"/>
          </div>
        </div>

        <div class="space-y-1">
          <label for="confirmation" class="block text-sm font-medium text-gray-700">Repeat password</label>
          <div class="mt-1 group relative inline-block w-full">
            <Field id="confirmation" name="confirmation" type="password" autocomplete="confirmation" class="block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 placeholder-gray-400 shadow-sm focus:border-rose-600 focus:outline-none focus:ring-rose-600 sm:text-sm" />
            <ErrorMessage name="confirmation" class="absolute left-5 top-5 translate-y-full w-48 px-2 py-1 bg-gray-700 rounded-lg text-center text-white text-sm after:content-[''] after:absolute after:left-1/2 after:bottom-[100%] after:-translate-x-1/2 after:border-8 after:border-x-transparent after:border-t-transparent after:border-b-gray-700"/>
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

const schema = {
  password: { required: false, min: 8 },
  confirmation: { required: false, confirmed: "password" }
}

const auth = useAuthStore()
let profile = {} as IUserProfileUpdate
const title = "Password"
const description = "Update your password. Make it long and strong."


onMounted( () => {
  resetProfile()
})

function resetProfile() {
  profile = {
    password: ""
  }
}

async function submit(values: any, { resetForm }) {
  profile = {}
  if (values.password) {
    profile.password = values.password
    await auth.updateUserProfile(profile)
    resetForm()
  }
}
</script>