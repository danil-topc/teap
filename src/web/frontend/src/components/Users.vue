<template>
  <div>
    <h2>Users: </h2>
    <!-- Users list -->
    <div>
      <p>List:</p>
      <ul>
        <li v-for="user in users" :key="user.fqdn">
          <router-link :to="{name: 'user', params: {id: user.uid}}">{{ user.uid }}</router-link> <button v-on:click="deleteUser(user)">delete</button>
        </li>
      </ul>
    </div>
    <router-link :to="{name: 'newUser'}"><a>New user</a></router-link>
  </div>
</template>

<script>
import { LdapUsersService } from '../common/ldap-api.service.js'

export default {
  data () {
    return {
      users: null
    }
  },
  methods: {
    getUsers () {
      LdapUsersService.get()
        .then(response => {
          this.users = response.data
        }
        )
        .catch((error) => {
          this.$notifier.error({text: error.response.data.message})
        })
    },
    deleteUser (user) {
      if (!confirm('Are you sure you want to delete this user?')) {
        return
      }
      LdapUsersService.delete(user.uid)
        .then(response => {
          this.$notifier.success({text: 'User successfully deleted'})
        }, error => {
          this.$notifier.error({title: 'Failed to delete', text: error.response.data.message})
        })
        .catch((error) => {
          this.$notifier.error({text: error.response.data.message})
        })
        .finally(response => {
          this.getUsers()
        })
    }

  },
  created () {
    this.getUsers()
  }
}
</script>
