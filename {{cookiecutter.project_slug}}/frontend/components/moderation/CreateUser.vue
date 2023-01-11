<template>
    <div class="shadow sm:overflow-hidden sm:rounded-md min-w-max">
      <Form @submit="submit" :validation-schema="schema">
        <div class="space-y-6 bg-white py-6 px-4 sm:p-6">
          <div>
            <label for="full_name" class="block text-sm font-medium text-gray-700">Profile name</label>
            <div class="mt-1 group relative inline-block w-full">
              <Field 
                id="full_name" 
                name="full_name" 
                type="string"
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
import { apiAuth } from "@/api"
import { useTokenStore, useToastStore } from "@/stores"
import { generateUUID } from "@/utilities"
import { IUserProfileCreate } from "@/interfaces"

const schema = {
    full_name: { required: false },
    email: { email: true, required: true },
}
const token = useTokenStore()
const toast = useToastStore()

// @ts-ignore
async function submit(values: any, { resetForm }) {
  if (values.email) {
    await token.refreshTokens()
    const data: IUserProfileCreate = {
        email: values.email,
        password: generateUUID(),
        full_name: values.full_name ? values.full_name : ""
    }
    const { data: response } = await apiAuth.createUserProfile(token.token, data)
    if (!response.value) {
        toast.addNotice({
            title: "Update error",
            content: "Invalid request.",
            icon: "error"
        })
    } else {
      toast.addNotice({
            title: "User created",
            content: "An email has been sent to the user with their new login details."
        })
      resetForm()
    }
  }
}
</script>