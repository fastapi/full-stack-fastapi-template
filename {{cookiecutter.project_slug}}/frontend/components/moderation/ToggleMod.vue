<template>
    <ModerationCheckToggle :check="props.check" @click="submit" />
</template>

<script setup lang="ts">
import { apiAuth } from "@/api"
import { useTokenStore, useToastStore } from "@/stores"
import { IUserProfileUpdate } from "@/interfaces"

const token = useTokenStore()
const toast = useToastStore()
const checkState = ref(false)
const props = defineProps({
    email: String,
    check: Boolean
})

async function submit() {
    await token.refreshTokens()
    const data: IUserProfileUpdate = {
        email: props.email,
        is_superuser: !props.check
    }
    const { data: response } = await apiAuth.toggleUserState(token.token, data)
    if (!response.value || !response.value.msg) {
        toast.addNotice({
            title: "Update error",
            content: response.value ? response.value.msg : "Invalid request.",
            icon: "error"
        })
        checkState.value = props.check
    }
}

onMounted(async () => {
    checkState.value = props.check
})
</script>