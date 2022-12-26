<template>
    <div class="bg-white">
        <slot name="header" >
            <LayoutsDefaultNavigation />
        </slot>
        <main>
            <ContentDoc />
        </main>
        <slot name="footer" >
            <LayoutsNotification />
            <LayoutsDefaultFooter />
        </slot>
    </div>
</template>