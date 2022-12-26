<template>
    <div class="h-full">
        <slot />
        <slot name="footer" >
            <LayoutsNotification />
        </slot>
    </div>
</template>