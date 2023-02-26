<template>
  <div class="relative isolate bg-white">
    <div class="mx-auto grid max-w-7xl grid-cols-1 lg:grid-cols-2">
      <div class="relative px-6 pt-24 pb-20 sm:pt-32 lg:static lg:py-48 lg:px-8">
        <div class="mx-auto max-w-xl lg:mx-0 lg:max-w-lg">
          <div
            class="absolute inset-y-0 left-0 -z-10 w-full overflow-hidden bg-gray-100 ring-1 ring-gray-900/10 lg:w-1/2">
            <svg
              class="absolute inset-0 h-full w-full stroke-gray-200 [mask-image:radial-gradient(100%_100%_at_top_right,white,transparent)]"
              aria-hidden="true">
              <defs>
                <pattern id="83fd4e5a-9d52-42fc-97b6-718e5d7ee527" width="200" height="200" x="100%" y="-1"
                  patternUnits="userSpaceOnUse">
                  <path d="M130 200V.5M.5 .5H200" fill="none" />
                </pattern>
              </defs>
              <rect width="100%" height="100%" stroke-width="0" fill="white" />
              <svg x="100%" y="-1" class="overflow-visible fill-gray-50">
                <path d="M-470.5 0h201v201h-201Z" stroke-width="0" />
              </svg>
              <rect width="100%" height="100%" stroke-width="0" fill="url(#83fd4e5a-9d52-42fc-97b6-718e5d7ee527)" />
            </svg>
          </div>
          <h2 class="text-3xl font-bold tracking-tight text-gray-900">Get in touch</h2>
          <p class="mt-6 text-lg leading-8 text-gray-600">
            We would love to hear from you.
          </p>
          <dl class="mt-10 space-y-4 text-base leading-7 text-gray-600">
            <div class="flex gap-x-4">
              <dt class="flex-none">
                <span class="sr-only">Telephone</span>
                <BuildingOffice2Icon class="h-7 w-6 text-gray-400" aria-hidden="true" />
              </dt>
              <dd>545 Mavis Island<br />Chicago, IL 99191</dd>
            </div>
            <div class="flex gap-x-4">
              <dt class="flex-none">
                <span class="sr-only">Telephone</span>
                <PhoneIcon class="h-7 w-6 text-gray-400" aria-hidden="true" />
              </dt>
              <dd><a class="hover:text-gray-900" href="tel:+1 (555) 234-5678">+1 (555) 234-5678</a></dd>
            </div>
            <div class="flex gap-x-4">
              <dt class="flex-none">
                <span class="sr-only">Telephone</span>
                <EnvelopeIcon class="h-7 w-6 text-gray-400" aria-hidden="true" />
              </dt>
              <dd><a class="hover:text-gray-900" href="mailto:hello@example.com">hello@example.com</a></dd>
            </div>
          </dl>
          <p class="mt-6 text-sm leading-8 text-gray-600">
            We care about your data. Read our <NuxtLink to="/privacy" class="font-semibold hover:text-indigo-600">privacy
              policy</NuxtLink>.
          </p>
        </div>
      </div>
      <Form @submit="submit" :validation-schema="schema" class="px-6 pb-24 pt-20 sm:pb-32 lg:py-48 lg:px-8">
        <div class="mx-auto max-w-xl lg:mr-0 lg:max-w-lg">
          <div class="space-y-6">
            <div>
              <label for="email-address" class="block text-sm font-medium text-gray-700">Email address</label>
              <div class="mt-2.5 group relative inline-block w-full">
                <Field id="email-address" name="email" type="email" autocomplete="email" placeholder="Enter your email"
                  class="block w-full rounded-md border-0 py-2 px-3.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" />
                <ErrorMessage name="email"
                  class="absolute left-5 top-5 translate-y-full w-48 px-2 py-1 bg-gray-700 rounded-lg text-center text-white text-sm after:content-[''] after:absolute after:left-1/2 after:bottom-[100%] after:-translate-x-1/2 after:border-8 after:border-x-transparent after:border-t-transparent after:border-b-gray-700" />
              </div>
            </div>
            <div>
              <label for="contact-message" class="block text-sm font-medium text-gray-700">Message</label>
              <div class="mt-2.5 group relative inline-block w-full">
                <Field id="contact-message" name="message" as="textarea" rows="4" placeholder="Enter your message"
                  class="block w-full rounded-md border-0 py-2 px-3.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" />
                <ErrorMessage name="message"
                  class="absolute left-5 top-5 translate-y-full w-48 px-2 py-1 bg-gray-700 rounded-lg text-center text-white text-sm after:content-[''] after:absolute after:left-1/2 after:bottom-[100%] after:-translate-x-1/2 after:border-8 after:border-x-transparent after:border-t-transparent after:border-b-gray-700" />
              </div>
            </div>
          </div>
          <div class="mt-8 flex justify-end">
            <button type="submit"
              class="rounded-md bg-indigo-600 px-3.5 py-2.5 text-center text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">Send
              message</button>
          </div>
        </div>
      </Form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { BuildingOffice2Icon, EnvelopeIcon, PhoneIcon } from "@heroicons/vue/24/outline"
import { ISendEmail } from "@/interfaces"
import { useToastStore, useAuthStore } from "@/stores"
import { apiService } from "@/api"

const toasts = useToastStore()
const auth = useAuthStore()

const schema = {
  email: { email: true, required: true },
  message: { required: true },
}

async function submit(values: any) {
  const data: ISendEmail = {
    email: values.email,
    subject: `Website contact from: ${values.email} `,
    content: values.message,
  }
  try {
    await apiService.postEmailContact(data)
    toasts.addNotice({
      title: "Message sent",
      content: "Thanks so much for contacting us.",
    })
    navigateTo("/")
  } catch (error) {
    toasts.addNotice({
      title: "Contact error",
      content: "Something went wrong with your email. Please check your details, or internet connection, and try again.",
      icon: "error"
    })
  }
}
</script>
