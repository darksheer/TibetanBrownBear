<template>
  <div>
    <h2>Administration</h2>
    <p>Customize Yeti's behavior. Get a glimpse of existing tags, manage Users,
    do other awesome things...</p>
    <nav class="nav nav-pills nav-fill">
      <router-link class="nav-item nav-link active" :to="{name: 'Tags'}">Tags</router-link>
      <a class="nav-item nav-link disabled" href="#">Users</a>
      <a class="nav-item nav-link disabled" href="#">Settings</a>
    </nav>
    <router-view />
  </div>
</template>

<script>
export default {
}
</script>

<style lang="css">
</style>
