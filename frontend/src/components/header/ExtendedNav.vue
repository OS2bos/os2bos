<template>
  <section class="extended-nav" v-if="is_enabled">
    <button class="extended-nav-toggle link-btn" @click.stop="openNav" title="Flere muligheder">
      <span class="material-icons extended-nav-toggle-icon">
        more_vert
      </span>
    </button>
    <div v-if="is_open" class="extended-nav-list">
      <a v-if="user.profile === 'workflow_engine'" href="/api/admin/">Klassifikationer</a>
      <a v-if="user.profile === 'admin'" href="/api/admin/">Administration</a>
      <router-link v-if="config.ALLOW_CHARTS" to="/dash/">Økonomisk overblik</router-link>
      <router-link v-if="user.profile === 'admin'" to="/export/">DST export</router-link>
    </div>
  </section>
</template>

<script>
export default {
  data: function() {
    return {
      is_open: false
    }
  },
  computed: {
    config: function() {
      return this.$store.getters.getConfig
    },
    user: function() {
      return this.$store.getters.getUser
    },
    is_enabled: function() {
      if (this.config && this.user) {
        if (this.config.ALLOW_CHARTS || this.user.profile === 'admin' || this.user.profile === 'workflow_engine') {
          return true
        } else {
          return false
        }
      } else {
        return false
      }
    }
  },
  methods: {
    openNav: function() {
      this.is_open = true
    }
  },
  mounted: function() {
    document.addEventListener('click', (ev) => {
      this.is_open = false
    })
  }
}
</script>

<style>

  .extended-nav {
    position: relative;
    display: inline-block;
  }

  .extended-nav-toggle {
    box-shadow: none;
    display: flex;
    flex-flow: column nowrap;
    align-items: center;
    justify-content: center;
    border: solid 1px transparent;
  }

  .extended-nav-toggle:hover,
  .extended-nav-toggle:active,
  .extended-nav-toggle:focus {
    color: var(--grey10);
    box-shadow: none;
  }

  .extended-nav-list {
    position: absolute;
    top: 2.5rem;
    right: 0;
    background-color: var(--grey0);
    box-shadow: var(--shadow-dim);
    min-width: 15rem;
  }

  .extended-nav-list > * {
    display: block;
    padding: .5rem 1rem;
  }

  .extended-nav-list a,
  .extended-nav-list a:link,
  .extended-nav-list a:visited {
    border-bottom: none;
  }
  .extended-nav-list a:hover,
  .extended-nav-list a:active,
  .extended-nav-list a:focus {
    background-color: var(--primary);
    color: var(--grey0);
  }

</style>
