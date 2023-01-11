<template>
  <div class="shadow sm:overflow-hidden sm:rounded-md max-w-lg">
    <Form @submit="submit" :validation-schema="schema">
      <div class="space-y-6 bg-white py-6 px-4 sm:p-6">
        <div>
          <h3 class="text-lg font-medium leading-6 text-gray-900">{{  title }}</h3>
          <p v-if="!auth.profile.password" class="mt-1 text-sm text-gray-500">
            Secure your account by adding a password, or enabling two-factor security. Or both. Any changes will 
            require you to enter your original password.
          </p>
          <p v-else class="mt-1 text-sm text-gray-500">
            Secure your account further by enabling two-factor security. Any changes will require you to enter 
            your original password.
          </p>
        </div>

        <div class="space-y-1">
          <label for="original" class="block text-sm font-medium text-gray-700">Original password</label>
          <div class="mt-1 group relative inline-block w-full">
            <Field id="original" name="original" type="password" autocomplete="password" class="block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 placeholder-gray-400 shadow-sm focus:border-rose-600 focus:outline-none focus:ring-rose-600 sm:text-sm" />
            <ErrorMessage name="original" class="absolute left-5 top-5 translate-y-full w-48 px-2 py-1 bg-gray-700 rounded-lg text-center text-white text-sm after:content-[''] after:absolute after:left-1/2 after:bottom-[100%] after:-translate-x-1/2 after:border-8 after:border-x-transparent after:border-t-transparent after:border-b-gray-700"/>
          </div>
        </div>

        <div class="space-y-1">
          <div class="flex items-center justify-between">
            <p class="text-sm font-medium text-rose-500 align-middle">
              Use two-factor security
            </p>
            <Switch v-model="totpEnabled" class="group relative inline-flex h-5 w-10 flex-shrink-0 cursor-pointer items-center justify-center rounded-full focus:outline-none focus:ring-2 focus:ring-rose-600 focus:ring-offset-2">
              <span class="sr-only">Use setting</span>
              <span aria-hidden="true" class="pointer-events-none absolute h-full w-full rounded-md bg-white" />
              <span aria-hidden="true" :class="[totpEnabled ? 'bg-rose-500' : 'bg-gray-200', 'pointer-events-none absolute mx-auto h-4 w-9 rounded-full transition-colors duration-200 ease-in-out']" />
              <span aria-hidden="true" :class="[totpEnabled ? 'translate-x-5' : 'translate-x-0', 'pointer-events-none absolute left-0 inline-block h-5 w-5 transform rounded-full border border-gray-200 bg-white shadow ring-0 transition-transform duration-200 ease-in-out']" />
            </Switch>
        </div>
      </div>
        <div class="space-y-1">
          <label for="password" class="block text-sm font-medium text-gray-700">New password</label>
          <div class="mt-1 group relative inline-block w-full">
            <Field id="password" name="password" type="password" autocomplete="password" class="block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 placeholder-gray-400 shadow-sm focus:border-rose-600 focus:outline-none focus:ring-rose-600 sm:text-sm" />
            <ErrorMessage name="password" class="absolute left-5 top-5 translate-y-full w-48 px-2 py-1 bg-gray-700 rounded-lg text-center text-white text-sm after:content-[''] after:absolute after:left-1/2 after:bottom-[100%] after:-translate-x-1/2 after:border-8 after:border-x-transparent after:border-t-transparent after:border-b-gray-700"/>
          </div>
        </div>

        <div class="space-y-1">
          <label for="confirmation" class="block text-sm font-medium text-gray-700">Repeat new password</label>
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
    <TransitionRoot as="template" :show="totpModal">
    <Dialog as="div" class="relative z-10" @close="totpModal = false">
      <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0" enter-to="opacity-100" leave="ease-in duration-200" leave-from="opacity-100" leave-to="opacity-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
      </TransitionChild>

      <div class="fixed inset-0 z-10 overflow-y-auto">
        <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
          <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95" enter-to="opacity-100 translate-y-0 sm:scale-100" leave="ease-in duration-200" leave-from="opacity-100 translate-y-0 sm:scale-100" leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95">
            <DialogPanel class="relative transform overflow-hidden rounded-lg bg-white px-4 pt-5 pb-4 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
              <div class="sm:flex sm:items-start">
                <div class="mx-auto flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10">
                  <QrCodeIcon class="h-6 w-6 text-rose-500" aria-hidden="true" />
                </div>
                <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
                  <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900">Enable two-factor security</DialogTitle>
                  <div class="mt-2 max-w-lg">
                    <ul role="list" class="space-y-3">
                      <li class="flex items-start">
                        <div class="flex-shrink-0">
                          1
                        </div>
                        <p class="ml-3 text-sm leading-6 text-gray-600">
                          Download an authenticator app that supports Time-based One-Time Password (TOTP) for your mobile
                          device.
                        </p>
                      </li>
                      <li class="flex items-start">
                        <div class="flex-shrink-0">
                          2
                        </div>
                        <div class="ml-3 text-sm leading-6 text-gray-600">
                          <p>
                            Open the app and scan the QR code below to pair your mobile with your account.
                          </p>
                          <QrcodeVue :value="totpNew.uri" :size="qrSize" level="M" render-as="svg" class="my-2 mx-auto"/>
                          <p>
                            If you can't scan, you can type in the following key:
                          </p>
                          <p class="text-md font-semibold my-2 text-center">{{ totpNew.key }}</p>
                        </div>
                      </li>
                      <li class="flex items-start">
                        <div class="flex-shrink-0">
                          3
                        </div>
                        <div class="ml-3 text-sm leading-6 text-gray-600">
                          <p>
                            Enter the code generated by your Authenticator app below to pair your account:
                          </p>
                          <Form @submit="enableTOTP" :validation-schema="totpSchema">
                            <div class="space-y-1">
                              <label for="claim" class="block text-sm font-medium text-gray-700 mt-4">6-digit verification code</label>
                              <div class="mt-1 group relative inline-block w-full">
                                <Field id="claim" name="claim" type="text" autocomplete="off" class="block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 placeholder-gray-400 shadow-sm focus:border-rose-600 focus:outline-none focus:ring-rose-600 sm:text-sm" />
                              </div>
                            </div>
                            <div class="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse">
                              <button type="submit" class="inline-flex w-full justify-center rounded-md border border-transparent bg-rose-500 px-4 py-2 text-base font-medium text-white shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 sm:ml-3 sm:w-auto sm:text-sm">
                                Submit
                              </button>
                              <button type="button" class="mt-3 inline-flex w-full justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-base font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:mt-0 sm:w-auto sm:text-sm" 
                                @click="totpModal = false" 
                                ref="cancelButtonRef">
                                Cancel
                              </button>
                            </div>
                          </Form>
                        </div>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
  </div>
</template>

<script setup lang="ts">
import { Switch, Dialog, DialogPanel, DialogTitle, TransitionChild, TransitionRoot } from "@headlessui/vue"
import { QrCodeIcon } from "@heroicons/vue/24/outline"
import QrcodeVue from "qrcode.vue"
import { useAuthStore } from "@/stores"
import { apiAuth } from "@/api"
import { IUserProfileUpdate, INewTOTP, IEnableTOTP } from "@/interfaces"


const auth = useAuthStore()
let profile = {} as IUserProfileUpdate
const title = "Security"
const redirectTOTP = "/settings"
const totpEnabled = ref(false)
const totpModal = ref(false)
const totpNew = ref({} as INewTOTP)
const totpClaim = ref({} as IEnableTOTP)
const qrSize = 200

const schema = {
  original: { required: auth.profile.password, min: 8, max: 64 },
  password: { required: false, min: 8, max: 64 },
  confirmation: { required: false, confirmed: "password" }
}

const totpSchema = {
  claim: { required: true, min: 6, max: 7 }
}

onMounted( () => {
  resetProfile()
  totpEnabled.value = auth.profile.totp
})

function resetProfile() {
  profile = {
    password: ""
  }
}

// @ts-ignore
async function enableTOTP(values: any, { resetForm }) {
  totpClaim.value.claim = values.claim
  await auth.enableTOTPAuthentication(totpClaim.value)
  resetForm()
  totpModal.value = false 
}

// @ts-ignore
async function submit(values: any, { resetForm }) {
  profile = {}
  if ((!auth.profile.password && !values.original) || 
      (auth.profile.password && values.original)) {
    if (values.original) profile.original = values.original
    if (values.password && values.password !== values.original) {
      profile.password = values.password
      await auth.updateUserProfile(profile)
    }
    if (totpEnabled.value !== auth.profile.totp && totpEnabled.value) {
      await auth.authTokens.refreshTokens()
      const { data: response } = await apiAuth.requestNewTOTP(auth.authTokens.token)
      if (response.value) {
        totpNew.value.key = response.value.key
        totpNew.value.uri = response.value.uri
        totpClaim.value.uri = response.value.uri
        totpClaim.value.password = values.original
        totpModal.value = true
      }
    }
    if (totpEnabled.value !== auth.profile.totp && !totpEnabled.value) {
      await auth.disableTOTPAuthentication(profile)
    }
    resetForm()
  }

}
</script>