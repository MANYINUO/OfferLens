import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from './views/DashboardView.vue'
import ApplicationsView from './views/ApplicationsView.vue'
import MatchView from './views/MatchView.vue'
import ResumesView from './views/ResumesView.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'dashboard', component: DashboardView, meta: { title: '总览' } },
    { path: '/applications', name: 'applications', component: ApplicationsView, meta: { title: '投递记录' } },
    { path: '/match', name: 'match', component: MatchView, meta: { title: 'AI 职位匹配' } },
    { path: '/resumes', name: 'resumes', component: ResumesView, meta: { title: '简历版本' } },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})
