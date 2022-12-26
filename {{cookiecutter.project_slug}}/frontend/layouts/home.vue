<template>
    <div class="bg-white">
        <slot name="header" >
            <LayoutsHomeNavigation />
        </slot>
        <slot />
        <slot name="footer" >
            <LayoutsNotification />
            <LayoutsDefaultFooter />
        </slot>
    </div>
</template>