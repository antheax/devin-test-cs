<template>
  <div class="application-records container">
    <h1>申请记录</h1>
    <p class="slogan">高效管理，轻松申请</p>
    
    <div class="filters">
      <div class="month-filter">
        <label>按月份筛选：</label>
        <select v-model="selectedMonth" @change="fetchApplications">
          <option v-for="month in months" :key="month.value" :value="month.value">
            {{ month.label }}
          </option>
        </select>
      </div>
      
      <!-- New project filter -->
      <div class="project-filter">
        <label>按项目筛选：</label>
        <select v-model="selectedProject" @change="fetchApplications">
          <option value="">全部项目</option>
          <option v-for="project in projects" :key="project" :value="project">
            {{ project }}
          </option>
        </select>
      </div>
      
      <div class="actions">
        <button 
          v-if="currentUser && (currentUser.user_type === '超级管理员' || currentUser.user_type === '项目管理员')"
          class="btn btn-secondary" 
          @click="inheritPreviousMonth">继承上月用户名单</button>
        <button class="btn btn-primary" @click="showAddApplicationForm = true">新建申请</button>
      </div>
    </div>
    
    <table class="table">
      <thead>
        <tr>
          <th>申请日期</th>
          <th>用户</th>
          <th>项目</th>  <!-- New column -->
          <th>目标产品</th>
          <th>申请状态</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="application in applications" :key="application.id">
          <td>{{ formatDate(application.application_date) }}</td>
          <td>{{ application.user_name }}</td>
          <td>{{ application.project }}</td>  <!-- Display project -->
          <td>{{ application.target_product }}</td>
          <td>
            <span :class="['status', application.status === '已完成' ? 'completed' : 'pending']">
              {{ application.status }}
            </span>
          </td>
          <td>
            <button class="btn btn-primary" @click="editApplication(application)">编辑</button>
            <button class="btn btn-danger" @click="deleteApplication(application.id)">删除</button>
          </td>
        </tr>
      </tbody>
    </table>
    
    <div v-if="applications.length === 0" class="no-data">
      该月份没有申请记录
    </div>
    
    <!-- 添加申请表单 -->
    <div v-if="showAddApplicationForm" class="modal">
      <div class="modal-content">
        <h2>新建申请</h2>
        <form @submit.prevent="addApplication">
          <div class="form-group">
            <label>申请日期</label>
            <input v-model="newApplication.application_date" type="date" required />
          </div>
          <div class="form-group">
            <label>用户</label>
            <select v-model="newApplication.user_id" required>
              <option v-for="user in users" :key="user.id" :value="user.id">
                {{ user.name }} ({{ user.email }})
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>目标产品</label>
            <select v-model="newApplication.target_product" required>
              <option value="C">C</option>
              <option value="W">W</option>
            </select>
          </div>
          <div class="form-group">
            <label>申请状态</label>
            <select v-model="newApplication.status" required>
              <option value="申请中">申请中</option>
              <option value="已完成">已完成</option>
            </select>
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary">保存</button>
            <button type="button" class="btn" @click="showAddApplicationForm = false">取消</button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- 编辑申请表单 -->
    <div v-if="showEditApplicationForm" class="modal">
      <div class="modal-content">
        <h2>编辑申请</h2>
        <form @submit.prevent="updateApplication">
          <div class="form-group">
            <label>申请日期</label>
            <input v-model="editingApplication.application_date" type="date" required />
          </div>
          <div class="form-group">
            <label>用户</label>
            <select v-model="editingApplication.user_id" required>
              <option v-for="user in users" :key="user.id" :value="user.id">
                {{ user.name }} ({{ user.email }})
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>目标产品</label>
            <select v-model="editingApplication.target_product" required>
              <option value="C">C</option>
              <option value="W">W</option>
            </select>
          </div>
          <div class="form-group">
            <label>申请状态</label>
            <select v-model="editingApplication.status" required>
              <option value="申请中">申请中</option>
              <option value="已完成">已完成</option>
            </select>
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary">更新</button>
            <button type="button" class="btn" @click="showEditApplicationForm = false">取消</button>
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
      applications: [],
      users: [],
      selectedMonth: this.getCurrentMonth(),
      selectedProject: "", // New property for project filter
      months: this.generateMonths(),
      projects: [], // List to store unique projects
      showAddApplicationForm: false,
      showEditApplicationForm: false,
      newApplication: {
        application_date: new Date().toISOString().split('T')[0],
        user_id: null,
        target_product: 'C',
        status: '申请中'
      },
      editingApplication: null,
      currentUser: null
    };
  },
  created() {
    this.fetchCurrentUser();
    this.fetchApplications();
    this.fetchUsers();
    this.fetchProjects(); // Add this line
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
    async fetchApplications() {
      try {
        const response = await axios.get(
          `http://localhost:8000/applications?month=${this.selectedMonth}${
            this.selectedProject ? `&project=${this.selectedProject}` : ''
          }`, 
          {
            headers: {
              'user-id': this.currentUser ? this.currentUser.id : undefined
            }
          }
        );
        this.applications = response.data;
      } catch (error) {
        console.error('Error fetching applications:', error);
      }
    },
    
    async fetchProjects() {
      try {
        const response = await axios.get('http://localhost:8000/users', {
          headers: {
            'user-id': this.currentUser ? this.currentUser.id : undefined
          }
        });
        // Extract unique projects from users
        this.projects = [...new Set(response.data.map(user => user.project))];
      } catch (error) {
        console.error('Error fetching projects:', error);
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
        
        // Set default user if available
        if (this.users.length > 0 && !this.newApplication.user_id) {
          this.newApplication.user_id = this.users[0].id;
        }
      } catch (error) {
        console.error('Error fetching users:', error);
      }
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString('zh-CN');
    },
    getCurrentMonth() {
      const now = new Date();
      return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
    },
    generateMonths() {
      const months = [];
      const now = new Date();
      const currentYear = now.getFullYear();
      
      // Generate months for current year and previous year
      for (let year = currentYear; year >= currentYear - 1; year--) {
        for (let month = 12; month >= 1; month--) {
          const monthValue = `${year}-${String(month).padStart(2, '0')}`;
          const monthLabel = `${year}年${month}月`;
          months.push({ value: monthValue, label: monthLabel });
          
          // Stop when we reach current month for current year
          if (year === currentYear && month === now.getMonth() + 1) {
            break;
          }
        }
      }
      
      return months;
    },
    async addApplication() {
      try {
        await axios.post('http://localhost:8000/applications', this.newApplication, {
          headers: {
            'user-id': this.currentUser ? this.currentUser.id : undefined
          }
        });
        this.showAddApplicationForm = false;
        this.newApplication = {
          application_date: new Date().toISOString().split('T')[0],
          user_id: this.users.length > 0 ? this.users[0].id : null,
          target_product: 'C',
          status: '申请中'
        };
        this.fetchApplications();
      } catch (error) {
        console.error('Error adding application:', error);
        alert('添加申请失败: ' + (error.response?.data?.detail || error.message));
      }
    },
    editApplication(application) {
      this.editingApplication = { ...application };
      this.showEditApplicationForm = true;
    },
    async updateApplication() {
      try {
        await axios.put(`http://localhost:8000/applications/${this.editingApplication.id}`, this.editingApplication, {
          headers: {
            'user-id': this.currentUser ? this.currentUser.id : undefined
          }
        });
        this.showEditApplicationForm = false;
        this.editingApplication = null;
        this.fetchApplications();
      } catch (error) {
        console.error('Error updating application:', error);
        alert('更新申请失败: ' + (error.response?.data?.detail || error.message));
      }
    },
    async deleteApplication(applicationId) {
      if (confirm('确定要删除此申请记录吗？')) {
        try {
          await axios.delete(`http://localhost:8000/applications/${applicationId}`, {
            headers: {
              'user-id': this.currentUser ? this.currentUser.id : undefined
            }
          });
          this.fetchApplications();
        } catch (error) {
          console.error('Error deleting application:', error);
          alert('删除申请失败: ' + (error.response?.data?.detail || error.message));
        }
      }
    },
    async inheritPreviousMonth() {
      if (confirm('确定要从上个月继承用户名单吗？所有继承的记录状态将设置为"申请中"。')) {
        try {
          await axios.post(`http://localhost:8000/applications/inherit-previous-month`, 
            { current_month: this.selectedMonth },
            {
              headers: {
                'user-id': this.currentUser ? this.currentUser.id : undefined
              }
            }
          );
          this.fetchApplications();
        } catch (error) {
          console.error('Error inheriting applications:', error);
          alert('继承上月用户名单失败: ' + (error.response?.data?.detail || error.message));
        }
      }
    }
  }
};
</script>

<style scoped>
.filters {
  margin-bottom: 20px;
  display: flex;
  justify-content: flex-end;
}

.month-filter, .project-filter {
  display: flex;
  align-items: center;
  margin-right: 15px;
}

.month-filter label, .project-filter label {
  margin-right: 10px;
}

.month-filter select, .project-filter select {
  padding: 8px;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.status {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.status.completed {
  background-color: #67c23a;
  color: white;
}

.status.pending {
  background-color: #e6a23c;
  color: white;
}

.no-data {
  text-align: center;
  padding: 20px;
  color: #909399;
}

.slogan {
  text-align: center;
  margin-top: -10px;
  margin-bottom: 20px;
  color: #909399;
  font-size: 14px;
}
</style>
