<template>
  <div class="user-management container">
    <h1>用户管理</h1>
    
    <div class="actions">
      <button class="btn btn-primary" @click="showAddUserForm = true">添加用户</button>
    </div>
    
    <table class="table">
      <thead>
        <tr>
          <th>姓名</th>
          <th>邮箱</th>
          <th>租户</th>
          <th>部门</th>
          <th>项目</th>
          <th>项目角色</th>
          <th>用户类型</th>
          <th>Tabs Accepted</th>
          <th>Premium Requests Used</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.id">
          <td>{{ user.name }}</td>
          <td>{{ user.email }}</td>
          <td>{{ user.tenant }}</td>
          <td>{{ user.department }}</td>
          <td>{{ user.project }}</td>
          <td>{{ user.role }}</td>
          <td>{{ user.user_type }}</td>
          <td>{{ user.tabs_accepted }}</td>
          <td>{{ user.premium_requests_used }}</td>
          <td>
            <button class="btn btn-primary" @click="editUser(user)">编辑</button>
            <button class="btn btn-danger" @click="deleteUser(user.id)">删除</button>
          </td>
        </tr>
      </tbody>
    </table>
    
    <!-- 添加用户表单 -->
    <div v-if="showAddUserForm" class="modal">
      <div class="modal-content">
        <h2>添加用户</h2>
        <form @submit.prevent="addUser">
          <div class="form-group">
            <label>姓名</label>
            <input v-model="newUser.name" required />
          </div>
          <div class="form-group">
            <label>邮箱</label>
            <input v-model="newUser.email" type="email" required />
          </div>
          <div class="form-group">
            <label>租户</label>
            <input v-model="newUser.tenant" required />
          </div>
          <div class="form-group">
            <label>部门</label>
            <input v-model="newUser.department" required />
          </div>
          <div class="form-group">
            <label>项目</label>
            <input v-model="newUser.project" required />
          </div>
          <div class="form-group">
            <label>项目角色</label>
            <input v-model="newUser.role" required />
          </div>
          <div class="form-group">
            <label>用户类型</label>
            <select v-model="newUser.user_type" required>
              <option value="普通用户">普通用户</option>
              <option value="项目管理员">项目管理员</option>
              <option value="超级管理员">超级管理员</option>
            </select>
          </div>
          <div class="form-group">
            <label>Tabs Accepted</label>
            <input v-model.number="newUser.tabs_accepted" type="number" required />
          </div>
          <div class="form-group">
            <label>Premium Requests Used</label>
            <input v-model.number="newUser.premium_requests_used" type="number" required />
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary">保存</button>
            <button type="button" class="btn" @click="showAddUserForm = false">取消</button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- 编辑用户表单 -->
    <div v-if="showEditUserForm" class="modal">
      <div class="modal-content">
        <h2>编辑用户</h2>
        <form @submit.prevent="updateUser">
          <div class="form-group">
            <label>姓名</label>
            <input v-model="editingUser.name" required />
          </div>
          <div class="form-group">
            <label>邮箱</label>
            <input v-model="editingUser.email" type="email" required />
          </div>
          <div class="form-group">
            <label>租户</label>
            <input v-model="editingUser.tenant" required />
          </div>
          <div class="form-group">
            <label>部门</label>
            <input v-model="editingUser.department" required />
          </div>
          <div class="form-group">
            <label>项目</label>
            <input v-model="editingUser.project" required />
          </div>
          <div class="form-group">
            <label>项目角色</label>
            <input v-model="editingUser.role" required />
          </div>
          <div class="form-group">
            <label>用户类型</label>
            <select v-model="editingUser.user_type" required>
              <option value="普通用户">普通用户</option>
              <option value="项目管理员">项目管理员</option>
              <option value="超级管理员">超级管理员</option>
            </select>
          </div>
          <div class="form-group">
            <label>Tabs Accepted</label>
            <input v-model.number="editingUser.tabs_accepted" type="number" required />
          </div>
          <div class="form-group">
            <label>Premium Requests Used</label>
            <input v-model.number="editingUser.premium_requests_used" type="number" required />
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary">更新</button>
            <button type="button" class="btn" @click="showEditUserForm = false">取消</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      users: [],
      showAddUserForm: false,
      showEditUserForm: false,
      newUser: {
        name: '',
        email: '',
        tenant: '',
        department: '',
        project: '',
        role: '',
        user_type: '普通用户',
        tabs_accepted: 0,
        premium_requests_used: 0
      },
      editingUser: null,
      currentUser: null
    };
  },
  created() {
    this.fetchCurrentUser();
    this.fetchUsers();
  },
  methods: {
    async fetchCurrentUser() {
      try {
        // In a real app, this would be fetched from a login endpoint or session
        this.currentUser = { id: 1, user_type: '超级管理员' };
      } catch (error) {
        console.error('Error fetching current user:', error);
      }
    },
    async fetchUsers() {
      try {
        const response = await axios.get('http://localhost:8000/users', {
          headers: {
            'user-id': this.currentUser ? this.currentUser.id : undefined
          }
        });
        this.users = response.data;
      } catch (error) {
        console.error('Error fetching users:', error);
      }
    },
    async addUser() {
      try {
        await axios.post('http://localhost:8000/users', this.newUser, {
          headers: {
            'user-id': this.currentUser ? this.currentUser.id : undefined
          }
        });
        this.showAddUserForm = false;
        this.newUser = {
          name: '',
          email: '',
          tenant: '',
          department: '',
          project: '',
          role: '',
          user_type: '普通用户',
          tabs_accepted: 0,
          premium_requests_used: 0
        };
        this.fetchUsers();
      } catch (error) {
        console.error('Error adding user:', error);
        alert('添加用户失败: ' + (error.response?.data?.detail || error.message));
      }
    },
    editUser(user) {
      this.editingUser = { ...user };
      this.showEditUserForm = true;
    },
    async updateUser() {
      try {
        await axios.put(`http://localhost:8000/users/${this.editingUser.id}`, this.editingUser, {
          headers: {
            'user-id': this.currentUser ? this.currentUser.id : undefined
          }
        });
        this.showEditUserForm = false;
        this.editingUser = null;
        this.fetchUsers();
      } catch (error) {
        console.error('Error updating user:', error);
        alert('更新用户失败: ' + (error.response?.data?.detail || error.message));
      }
    },
    async deleteUser(userId) {
      if (confirm('确定要删除此用户吗？')) {
        try {
          await axios.delete(`http://localhost:8000/users/${userId}`, {
            headers: {
              'user-id': this.currentUser ? this.currentUser.id : undefined
            }
          });
          this.fetchUsers();
        } catch (error) {
          console.error('Error deleting user:', error);
          alert('删除用户失败: ' + (error.response?.data?.detail || error.message));
        }
      }
    }
  }
};
</script>

<style scoped>
.actions {
  margin-bottom: 20px;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  width: 500px;
  max-width: 90%;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-group input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}
</style>
