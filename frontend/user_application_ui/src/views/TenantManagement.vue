<template>
  <div class="tenant-management container">
    <h1>租户管理</h1>
    
    <div class="actions">
      <button class="btn btn-primary" @click="showAddTenantForm = true">添加租户</button>
    </div>
    
    <table class="table">
      <thead>
        <tr>
          <th>租户名称</th>
          <th>更新周期（天）</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="tenant in tenants" :key="tenant.id">
          <td>{{ tenant.name }}</td>
          <td>{{ tenant.update_cycle }}</td>
          <td>
            <button class="btn btn-primary" @click="editTenant(tenant)">编辑</button>
            <button class="btn btn-danger" @click="deleteTenant(tenant.id)">删除</button>
          </td>
        </tr>
      </tbody>
    </table>
    
    <div v-if="tenants.length === 0" class="no-data">
      暂无租户数据
    </div>
    
    <!-- 添加租户表单 -->
    <div v-if="showAddTenantForm" class="modal">
      <div class="modal-content">
        <h2>添加租户</h2>
        <form @submit.prevent="addTenant">
          <div class="form-group">
            <label>租户名称</label>
            <input v-model="newTenant.name" required />
          </div>
          <div class="form-group">
            <label>更新周期（天）</label>
            <input v-model.number="newTenant.update_cycle" type="number" min="1" required />
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary">保存</button>
            <button type="button" class="btn" @click="showAddTenantForm = false">取消</button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- 编辑租户表单 -->
    <div v-if="showEditTenantForm" class="modal">
      <div class="modal-content">
        <h2>编辑租户</h2>
        <form @submit.prevent="updateTenant">
          <div class="form-group">
            <label>租户名称</label>
            <input v-model="editingTenant.name" required />
          </div>
          <div class="form-group">
            <label>更新周期（天）</label>
            <input v-model.number="editingTenant.update_cycle" type="number" min="1" required />
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary">更新</button>
            <button type="button" class="btn" @click="showEditTenantForm = false">取消</button>
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
      tenants: [],
      showAddTenantForm: false,
      showEditTenantForm: false,
      newTenant: {
        name: '',
        update_cycle: 30
      },
      editingTenant: null,
      currentUser: null
    };
  },
  created() {
    this.fetchCurrentUser();
    this.fetchTenants();
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
    async fetchTenants() {
      try {
        const response = await axios.get('http://localhost:8000/tenants', {
          headers: {
            'user-id': this.currentUser ? this.currentUser.id : undefined
          }
        });
        this.tenants = response.data;
      } catch (error) {
        console.error('Error fetching tenants:', error);
      }
    },
    async addTenant() {
      try {
        await axios.post('http://localhost:8000/tenants', this.newTenant, {
          headers: {
            'user-id': this.currentUser ? this.currentUser.id : undefined
          }
        });
        this.showAddTenantForm = false;
        this.newTenant = {
          name: '',
          update_cycle: 30
        };
        this.fetchTenants();
      } catch (error) {
        console.error('Error adding tenant:', error);
        alert('添加租户失败: ' + (error.response?.data?.detail || error.message));
      }
    },
    editTenant(tenant) {
      this.editingTenant = { ...tenant };
      this.showEditTenantForm = true;
    },
    async updateTenant() {
      try {
        await axios.put(`http://localhost:8000/tenants/${this.editingTenant.id}`, this.editingTenant, {
          headers: {
            'user-id': this.currentUser ? this.currentUser.id : undefined
          }
        });
        this.showEditTenantForm = false;
        this.editingTenant = null;
        this.fetchTenants();
      } catch (error) {
        console.error('Error updating tenant:', error);
        alert('更新租户失败: ' + (error.response?.data?.detail || error.message));
      }
    },
    async deleteTenant(tenantId) {
      if (confirm('确定要删除此租户吗？')) {
        try {
          await axios.delete(`http://localhost:8000/tenants/${tenantId}`, {
            headers: {
              'user-id': this.currentUser ? this.currentUser.id : undefined
            }
          });
          this.fetchTenants();
        } catch (error) {
          console.error('Error deleting tenant:', error);
          alert('删除租户失败: ' + (error.response?.data?.detail || error.message));
        }
      }
    }
  }
};
</script>

<style scoped>
.actions {
  margin-bottom: 20px;
  display: flex;
  justify-content: flex-end;
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

.btn {
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  border: none;
}

.btn-primary {
  background-color: #409eff;
  color: white;
}

.btn-danger {
  background-color: #f56c6c;
  color: white;
}

.no-data {
  text-align: center;
  padding: 20px;
  color: #909399;
}
</style>
