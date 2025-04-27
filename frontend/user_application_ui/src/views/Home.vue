<template>
  <div class="home container">
    <h1>用户账号申请管理</h1>
    <p>欢迎使用用户账号申请管理，您可以管理用户信息和查看申请记录。</p>
    <div class="features">
      <div class="feature">
        <h3>用户管理</h3>
        <p>添加、编辑和删除用户信息，包括租户、部门、项目等信息。</p>
        <router-link to="/users" class="btn btn-primary">进入用户管理</router-link>
      </div>
      <div class="feature">
        <h3>申请记录</h3>
        <p>查看和管理用户的申请记录，按月份筛选查看。</p>
        <router-link to="/applications" class="btn btn-primary">查看申请记录</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home {
  text-align: center;
}

.features {
  display: flex;
  justify-content: center;
  margin-top: 40px;
  gap: 30px;
}

.feature {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  width: 300px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style>
