<template>
    <div class="bg-white">
        <slot name="header" >
            <LayoutsDefaultNavigation />
        </slot>
        <slot />
        <slot name="footer" >
            <LayoutsNotification />
            <LayoutsDefaultFooter />
        </slot>
    </div>
</template>