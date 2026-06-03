<template>
  <main v-if="!currentUser" class="login-shell">
    <div class="login-language">
      <el-button @click="toggleLanguage">{{ languageToggleLabel }}</el-button>
    </div>

    <section class="login-hero">
      <div class="login-copy">
        <p class="eyebrow">{{ t('loginEyebrow') }}</p>
        <h1>{{ t('loginTitle') }}</h1>
        <p>{{ t('loginSubtitle') }}</p>
        <div class="login-stats">
          <span>{{ t('loginStatOne') }}</span>
          <span>{{ t('loginStatTwo') }}</span>
          <span>{{ t('loginStatThree') }}</span>
        </div>
        <div class="login-product-preview" aria-hidden="true">
          <div class="preview-paper preview-paper-main">
            <span></span>
            <b></b>
            <i></i>
            <i></i>
            <i></i>
          </div>
          <div class="preview-paper preview-paper-side">
            <span></span>
            <i></i>
            <i></i>
          </div>
          <div class="preview-floating-chip">PDF</div>
          <div class="preview-floating-chip preview-chip-alt">ATS 92</div>
        </div>
      </div>

      <div class="login-panel" :class="{ 'login-panel-qr': qrMode }">
        <div v-if="!qrMode" class="login-panel-head">
          <div>
            <p class="eyebrow">{{ t('signIn') }}</p>
            <h2>{{ t('chooseLogin') }}</h2>
          </div>
        </div>

        <template v-if="!qrMode">
          <el-form label-position="top" class="email-login">
            <el-form-item :label="t('email')">
              <el-input v-model="emailForm.email" :placeholder="t('emailPlaceholder')" />
            </el-form-item>
            <div class="code-row">
              <el-form-item :label="t('code')">
                <el-input v-model="emailForm.code" :placeholder="t('codePlaceholder')" />
              </el-form-item>
              <el-button :loading="sendingCode" @click="sendCode">{{ t('sendCode') }}</el-button>
            </div>
            <p v-if="emailForm.devCode" class="dev-code">{{ t('demoCode') }} {{ emailForm.devCode }}</p>
            <el-button type="primary" :loading="loggingIn" @click="loginWithEmail">
              {{ t('emailRegister') }}
            </el-button>
          </el-form>

          <div class="login-divider">
            <span>{{ t('orThirdParty') }}</span>
          </div>

          <div class="social-login-row">
            <button class="social-login-button social-wechat" @click="openQrLogin('wechat')">
              <span></span>
              {{ t('wechatLogin') }}
            </button>
            <button class="social-login-button social-alipay" @click="openQrLogin('alipay')">
              <span></span>
              {{ t('alipayLogin') }}
            </button>
          </div>
        </template>

        <div v-else class="qr-login-dock">
          <button class="qr-back" @click="closeQrLogin">{{ t('backToLogin') }}</button>
          <p class="qr-title">{{ selectedQrProvider === 'wechat' ? t('wechatLogin') : t('alipayLogin') }}</p>
          <div class="qr-stage" :class="`qr-stage-${selectedQrProvider}`">
            <img v-if="qrImage" :src="qrImage" :alt="t('scanQr')" />
            <div v-else class="qr-loading">{{ t('qrLoading') }}</div>
          </div>
          <div class="qr-dots" role="tablist" :aria-label="t('chooseLogin')">
            <button
              v-for="provider in qrProviders"
              :key="provider"
              :class="[`qr-dot-${provider}`, { active: selectedQrProvider === provider }]"
              :aria-label="provider === 'wechat' ? t('wechatLogin') : t('alipayLogin')"
              @click="selectedQrProvider = provider"
            ></button>
          </div>
          <div class="qr-caption">
            <span>{{ t('scanToEnter') }}</span>
          </div>
        </div>
      </div>
    </section>
  </main>

  <main v-else class="app-shell">
    <aside class="sidebar">
      <div class="brand-block">
        <div class="brand-mark">AI</div>
        <div>
          <p class="eyebrow">{{ t('resumeStudio') }}</p>
          <h1>{{ t('careerPackBuilder') }}</h1>
        </div>
      </div>

      <section class="profile-card">
        <div class="photo-upload">
          <img v-if="photoDataUrl" :src="photoDataUrl" alt="Candidate portrait" />
          <UserFilled v-else class="photo-placeholder" />
          <input ref="photoInput" type="file" accept="image/*" @change="handlePhotoUpload" />
        </div>
        <el-button :icon="Upload" @click="photoInput?.click()">{{ t('uploadPhoto') }}</el-button>
        <el-button v-if="photoDataUrl" :icon="Delete" text @click="photoDataUrl = ''">{{ t('remove') }}</el-button>
      </section>

      <section class="score-card">
        <div>
          <p class="eyebrow">{{ t('resumeReadiness') }}</p>
          <strong>{{ resumeScore }}%</strong>
        </div>
        <el-progress :percentage="resumeScore" :stroke-width="9" :show-text="false" />
        <div class="score-grid">
          <span>{{ t('ats') }}</span>
          <b>{{ result ? t('ready') : t('draft') }}</b>
          <span>{{ t('photo') }}</span>
          <b>{{ photoDataUrl ? t('included') : t('optional') }}</b>
          <span>{{ t('export') }}</span>
          <b>PDF / DOCX / MD</b>
        </div>
      </section>

      <nav class="side-rail" aria-label="Workspace sections">
        <span :class="{ active: activeTask === 'resume_generate' }">{{ t('taskGenerate') }}</span>
        <span :class="{ active: activeTask === 'resume_optimize' }">{{ t('taskOptimize') }}</span>
        <span :class="{ active: activeTask === 'interview_questions' }">{{ t('taskInterview') }}</span>
        <span>{{ t('export') }}</span>
        <span>{{ t('history') }}</span>
      </nav>
    </aside>

    <section class="main-workspace">
      <header class="topbar">
        <div>
          <p class="eyebrow">{{ t('resumeStudio') }}</p>
          <h2>{{ t('appSubtitle') }}</h2>
          <div class="topbar-pills">
            <span>{{ sourceLabel }}</span>
            <span>{{ styleLabel }}</span>
            <span>{{ resumeScore }}%</span>
          </div>
        </div>
        <div class="topbar-actions">
          <el-button @click="toggleLanguage">{{ languageToggleLabel }}</el-button>
          <el-tag :type="sourceTagType" effect="light">
            {{ sourceLabel }}
          </el-tag>
          <el-button text @click="logout">{{ t('logout') }}</el-button>
        </div>
      </header>

      <div class="workspace-grid">
        <section class="task-panel">
          <el-segmented v-model="activeTask" :options="taskOptions" block />

          <div class="form-surface">
            <div class="task-heading">
              <component :is="taskMeta[activeTask].icon" />
              <div>
                <h3>{{ taskMeta[activeTask].title }}</h3>
                <p>{{ taskMeta[activeTask].subtitle }}</p>
              </div>
            </div>

            <el-form label-position="top">
              <template v-if="activeTask === 'resume_generate'">
                <div class="grid-2">
                  <el-form-item :label="t('name')">
                    <el-input v-model="forms.resume_generate.name" :placeholder="t('namePlaceholder')" />
                  </el-form-item>
                  <el-form-item :label="t('targetRole')">
                    <el-input v-model="forms.resume_generate.target_role" :placeholder="t('targetRolePlaceholder')" />
                  </el-form-item>
                  <el-form-item :label="t('email')">
                    <el-input v-model="forms.resume_generate.email" placeholder="alex@example.com" />
                  </el-form-item>
                  <el-form-item :label="t('phone')">
                    <el-input v-model="forms.resume_generate.phone" placeholder="+1 555 0100" />
                  </el-form-item>
                </div>
                <el-form-item :label="t('education')">
                  <el-input v-model="forms.resume_generate.education" type="textarea" :rows="3" />
                </el-form-item>
                <el-form-item :label="t('projects')">
                  <el-input v-model="forms.resume_generate.projects" type="textarea" :rows="5" />
                </el-form-item>
                <el-form-item :label="t('skills')">
                  <el-input v-model="forms.resume_generate.skills" type="textarea" :rows="3" />
                </el-form-item>
              </template>

              <template v-if="activeTask === 'resume_optimize'">
                <div class="grid-2">
                  <el-form-item :label="t('targetRole')">
                    <el-input v-model="forms.resume_optimize.target_role" :placeholder="t('optimizeRolePlaceholder')" />
                  </el-form-item>
                  <el-form-item :label="t('visualStyle')">
                    <el-select v-model="forms.resume_optimize.style">
                      <el-option :label="t('modern')" value="modern" />
                      <el-option :label="t('executive')" value="executive" />
                      <el-option :label="t('compactAts')" value="compact-ats" />
                    </el-select>
                  </el-form-item>
                </div>
                <el-form-item :label="t('resumeContentToBeautify')">
                  <el-input v-model="forms.resume_optimize.resume_text" type="textarea" :rows="12" />
                </el-form-item>
              </template>

              <template v-if="activeTask === 'interview_questions'">
                <div class="grid-2">
                  <el-form-item :label="t('jobTitle')">
                    <el-input v-model="forms.interview_questions.job_title" :placeholder="t('interviewRolePlaceholder')" />
                  </el-form-item>
                  <el-form-item :label="t('experienceLevel')">
                    <el-select v-model="forms.interview_questions.experience_level">
                      <el-option :label="t('entryLevel')" value="Entry level" />
                      <el-option :label="t('midLevel')" value="Mid level" />
                      <el-option :label="t('seniorLevel')" value="Senior level" />
                    </el-select>
                  </el-form-item>
                </div>
                <el-form-item :label="t('technicalDirection')">
                  <el-input v-model="forms.interview_questions.technical_direction" :placeholder="t('technicalDirectionPlaceholder')" />
                </el-form-item>
              </template>
            </el-form>
          </div>

          <div class="actions">
            <el-button :icon="RefreshLeft" @click="resetForm">{{ t('reset') }}</el-button>
            <el-button :icon="StarFilled" :disabled="!result" @click="prepareBeautify">{{ t('beautifyCurrent') }}</el-button>
            <el-button type="primary" :icon="MagicStick" :loading="loading" @click="submit">
              {{ t('generate') }}
            </el-button>
          </div>
        </section>

        <aside class="result-panel">
          <div class="panel-header">
            <div>
              <p class="eyebrow">{{ t('livePreview') }}</p>
              <h3>{{ taskMeta[activeTask].title }}</h3>
            </div>
            <div class="result-tools">
              <el-button :icon="CopyDocument" circle :disabled="!result" @click="copyResult" />
              <el-dropdown trigger="click" :disabled="!result" @command="downloadResult">
                <el-button type="primary" :icon="Download" :loading="exporting">
                  {{ t('export') }}
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="pdf">PDF</el-dropdown-item>
                    <el-dropdown-item command="docx">{{ t('wordDocx') }}</el-dropdown-item>
                    <el-dropdown-item command="md">{{ t('markdown') }}</el-dropdown-item>
                    <el-dropdown-item command="txt">{{ t('plainText') }}</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>

          <div v-if="result" class="resume-preview" :class="previewStyleClass">
            <div class="preview-header">
              <img v-if="photoDataUrl" :src="photoDataUrl" alt="Candidate portrait" />
              <div>
                <span>{{ forms.resume_generate.target_role || forms.resume_optimize.target_role || t('targetRole') }}</span>
                <strong>{{ candidateName }}</strong>
              </div>
            </div>
            <div class="style-strip">
              <span>{{ styleLabel }}</span>
              <i>{{ styleDescriptor }}</i>
            </div>
            <article v-html="renderedResult"></article>
          </div>
          <el-empty v-else :description="t('emptyPreview')" />
        </aside>
      </div>

      <section class="history-section">
        <div class="panel-header">
          <div>
            <p class="eyebrow">{{ t('history') }}</p>
            <h3>{{ t('recentGenerations') }}</h3>
          </div>
          <el-button :icon="Refresh" circle :loading="historyLoading" @click="loadHistory" />
        </div>
        <el-table :data="history" class="history-table" :empty-text="t('noHistory')">
          <el-table-column :label="t('task')" min-width="160">
            <template #default="{ row }">
              {{ formatTaskType(row.task_type) }}
            </template>
          </el-table-column>
          <el-table-column :label="t('preview')" min-width="360">
            <template #default="{ row }">
              <span class="preview-text">{{ row.content }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" :label="t('created')" min-width="180">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column :label="t('actions')" width="168" fixed="right">
            <template #default="{ row }">
              <el-button :icon="View" circle @click="useHistory(row)" />
              <el-button :icon="StarFilled" circle @click="beautifyHistory(row)" />
              <el-button :icon="Delete" circle type="danger" @click="removeHistory(row.id)" />
            </template>
          </el-table-column>
        </el-table>
      </section>
    </section>
  </main>
</template>

<script setup>
import { computed, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import QRCode from 'qrcode'
import {
  CopyDocument,
  Delete,
  DocumentChecked,
  Download,
  MagicStick,
  Refresh,
  RefreshLeft,
  StarFilled,
  Upload,
  UserFilled,
  View
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import {
  deleteHistoryRecord,
  exportDocument,
  createQrSession,
  generateContent,
  getQrSession,
  getHistory,
  requestEmailCode,
  verifyEmailCode
} from './api'

const messages = {
  en: {
    loginEyebrow: 'Secure entry',
    loginTitle: 'Sign in to your resume workspace',
    loginSubtitle: 'Scan with WeChat or Alipay, or register with an email verification code.',
    loginStatOne: 'AI resume builder',
    loginStatTwo: 'Multi-format export',
    loginStatThree: 'Bilingual workspace',
    signIn: 'Sign in',
    chooseLogin: 'Choose a login method',
    wechatLogin: 'WeChat scan login',
    alipayLogin: 'Alipay scan login',
    scanToEnter: 'Demo scan to enter',
    orEmail: 'or use email code',
    orScan: 'or scan below',
    orThirdParty: 'or continue with',
    backToLogin: 'Back to login',
    scanQr: 'Scan QR code',
    qrLoading: 'Generating QR...',
    email: 'Email',
    emailPlaceholder: 'you@example.com',
    code: 'Verification code',
    codePlaceholder: '6-digit code',
    sendCode: 'Send code',
    demoCode: 'Demo code:',
    emailRegister: 'Register / Sign in',
    resumeStudio: 'Resume Studio',
    careerPackBuilder: 'Career Pack Builder',
    uploadPhoto: 'Upload photo',
    remove: 'Remove',
    resumeReadiness: 'Resume readiness',
    ready: 'Ready',
    draft: 'Draft',
    photo: 'Photo',
    included: 'Included',
    optional: 'Optional',
    export: 'Export',
    appSubtitle: 'Build, refine, and export a focused resume workflow',
    openaiActive: 'OpenAI active',
    localModelActive: 'Local model active',
    freeLocalMode: 'Free local mode',
    demoMode: 'Free local mode',
    logout: 'Log out',
    codeSent: 'Verification code generated',
    loginSuccess: 'Signed in',
    enterEmail: 'Please enter your email',
    enterCode: 'Please enter the verification code',
    ats: 'ATS',
    name: 'Name',
    namePlaceholder: 'Alex Chen',
    targetRole: 'Target role',
    targetRolePlaceholder: 'Frontend Developer',
    optimizeRolePlaceholder: 'Data Analyst',
    phone: 'Phone',
    education: 'Education',
    projects: 'Projects',
    skills: 'Skills',
    resumeText: 'Resume text',
    visualStyle: 'Visual style',
    modern: 'Modern',
    executive: 'Executive',
    compactAts: 'Compact ATS',
    resumeContentToBeautify: 'Resume content to beautify',
    jobTitle: 'Job title',
    jobTitlePlaceholder: 'Product Intern',
    interviewRolePlaceholder: 'Backend Engineer',
    experienceLevel: 'Experience level',
    entryLevel: 'Entry level',
    midLevel: 'Mid level',
    seniorLevel: 'Senior level',
    technicalDirection: 'Technical direction',
    technicalDirectionPlaceholder: 'FastAPI, databases, REST APIs',
    reset: 'Reset',
    beautifyCurrent: 'Beautify current',
    generate: 'Generate',
    livePreview: 'Live preview',
    wordDocx: 'Word DOCX',
    markdown: 'Markdown',
    plainText: 'Plain text',
    emptyPreview: 'Generate a resume or interview kit to preview it here.',
    history: 'History',
    recentGenerations: 'Recent generations',
    noHistory: 'No history yet',
    task: 'Task',
    preview: 'Preview',
    created: 'Created',
    actions: 'Actions',
    taskGenerate: 'Generate',
    taskOptimize: 'Optimize & Style',
    taskBeautify: 'Beautify',
    taskInterview: 'Interview',
    resumeGenerator: 'Resume generator',
    resumeGeneratorSubtitle: 'Create a recruiter-ready resume from structured profile details.',
    resumeOptimizer: 'Resume optimizer and stylist',
    resumeOptimizerSubtitle: 'Rewrite, strengthen, and format resume text in one workflow.',
    oneClickBeautifier: 'One-click beautifier',
    oneClickBeautifierSubtitle: 'Turn the current draft into a polished, formatted resume layout.',
    interviewCoach: 'Interview coach',
    interviewCoachSubtitle: 'Prepare technical and behavioral questions with reference answers.',
    styleModernDescription: 'Editorial spacing, color accents, portfolio-ready rhythm',
    styleExecutiveDescription: 'Formal typography, strong contrast, leadership framing',
    styleCompactDescription: 'Dense structure, monochrome hierarchy, scanner-friendly',
    generatedSuccessfully: 'Generated successfully',
    generationFailed: 'Generation failed',
    copied: 'Copied',
    downloaded: 'Downloaded',
    exportFailed: 'Export failed',
    uploadImageOnly: 'Please upload an image file',
    imageTooLarge: 'Image must be smaller than 1.2 MB',
    deleted: 'Deleted',
    loginFailed: 'Login failed',
    codeRequestFailed: 'Code request failed',
    qrCodeFailed: 'QR code failed'
  },
  zh: {
    loginEyebrow: '安全入口',
    loginTitle: '登录你的简历工作台',
    loginSubtitle: '可使用微信或支付宝扫码登录，也可以通过邮箱验证码注册/登录。',
    loginStatOne: 'AI 简历生成',
    loginStatTwo: '多格式导出',
    loginStatThree: '中英文切换',
    signIn: '登录',
    chooseLogin: '选择登录方式',
    wechatLogin: '微信扫码登录',
    alipayLogin: '支付宝扫码登录',
    scanToEnter: '演示扫码进入',
    orEmail: '或使用邮箱验证码',
    orScan: '或使用下方扫码',
    orThirdParty: '或使用以下方式登录',
    backToLogin: '返回登录',
    scanQr: '扫描二维码',
    qrLoading: '正在生成二维码...',
    email: '邮箱',
    emailPlaceholder: 'you@example.com',
    code: '验证码',
    codePlaceholder: '6 位验证码',
    sendCode: '发送验证码',
    demoCode: '演示验证码：',
    emailRegister: '注册 / 登录',
    resumeStudio: '简历工作室',
    careerPackBuilder: '求职材料生成器',
    uploadPhoto: '上传照片',
    remove: '移除',
    resumeReadiness: '简历完成度',
    ready: '已就绪',
    draft: '草稿',
    photo: '照片',
    included: '已加入',
    optional: '可选',
    export: '导出',
    appSubtitle: '聚焦生成、优化并导出高质量简历',
    openaiActive: 'OpenAI 已启用',
    localModelActive: '本地模型已启用',
    freeLocalMode: '免费本地模式',
    demoMode: '免费本地模式',
    logout: '退出',
    codeSent: '验证码已生成',
    loginSuccess: '登录成功',
    enterEmail: '请输入邮箱',
    enterCode: '请输入验证码',
    ats: 'ATS',
    name: '姓名',
    namePlaceholder: '陈同学',
    targetRole: '目标岗位',
    targetRolePlaceholder: '前端开发工程师',
    optimizeRolePlaceholder: '数据分析师',
    phone: '电话',
    education: '教育经历',
    projects: '项目经历',
    skills: '技能',
    resumeText: '简历文本',
    visualStyle: '视觉风格',
    modern: '现代风',
    executive: '商务风',
    compactAts: '紧凑 ATS',
    resumeContentToBeautify: '需要美化的简历内容',
    jobTitle: '职位名称',
    jobTitlePlaceholder: '产品实习生',
    interviewRolePlaceholder: '后端工程师',
    experienceLevel: '经验等级',
    entryLevel: '初级',
    midLevel: '中级',
    seniorLevel: '高级',
    technicalDirection: '技术方向',
    technicalDirectionPlaceholder: 'FastAPI、数据库、REST API',
    reset: '重置',
    beautifyCurrent: '美化当前内容',
    generate: '生成',
    livePreview: '实时预览',
    wordDocx: 'Word DOCX',
    markdown: 'Markdown',
    plainText: '纯文本',
    emptyPreview: '生成简历或面试题后，会在这里预览。',
    history: '历史记录',
    recentGenerations: '最近生成',
    noHistory: '暂无历史记录',
    task: '任务',
    preview: '预览',
    created: '创建时间',
    actions: '操作',
    taskGenerate: '生成',
    taskOptimize: '优化美化',
    taskBeautify: '美化',
    taskInterview: '面试',
    resumeGenerator: '简历生成',
    resumeGeneratorSubtitle: '根据结构化资料生成适合招聘查看的简历。',
    resumeOptimizer: '简历优化美化',
    resumeOptimizerSubtitle: '一次完成内容改写、表达强化和版式风格整理。',
    oneClickBeautifier: '一键美化',
    oneClickBeautifierSubtitle: '把当前草稿整理成更精致的版式和表达。',
    interviewCoach: '面试助手',
    interviewCoachSubtitle: '生成技术题、行为题和参考回答。',
    styleModernDescription: '留白更舒适，带强调色，适合作品集式展示',
    styleExecutiveDescription: '正式排版，高对比，突出职业感和领导力表达',
    styleCompactDescription: '高密度、黑白结构，更适合 ATS 扫描',
    generatedSuccessfully: '生成成功',
    generationFailed: '生成失败',
    copied: '已复制',
    downloaded: '已下载',
    exportFailed: '导出失败',
    uploadImageOnly: '请上传图片文件',
    imageTooLarge: '图片大小必须小于 1.2 MB',
    deleted: '已删除',
    loginFailed: '登录失败',
    codeRequestFailed: '验证码请求失败',
    qrCodeFailed: '二维码生成失败'
  }
}

const defaultForms = {
  resume_generate: {
    name: 'Alex Chen',
    email: 'alex@example.com',
    phone: '+1 555 0100',
    education: 'B.S. in Computer Science, 2026. Coursework: data structures, databases, software engineering.',
    projects: 'Campus job board: built Vue pages, FastAPI endpoints, and PostgreSQL schema for job posts and applications.',
    skills: 'Vue, JavaScript, Python, FastAPI, SQL, Git',
    target_role: 'Frontend Developer',
    photo_data_url: ''
  },
  resume_optimize: {
    target_role: 'Frontend Developer',
    style: 'modern',
    resume_text: 'I made a website for students to find jobs. I used Vue and Python. I worked with classmates and fixed bugs.'
  },
  resume_beautify: {
    target_role: 'Frontend Developer',
    style: 'modern',
    resume_text: 'Paste or generate a resume first, then use this tool to make it cleaner and more polished.',
    photo_included: false
  },
  interview_questions: {
    job_title: 'Frontend Developer Intern',
    technical_direction: 'Vue 3, JavaScript, REST APIs, browser performance',
    experience_level: 'Entry level'
  }
}

const cloneDefaults = () => JSON.parse(JSON.stringify(defaultForms))
const forms = reactive(cloneDefaults())
const activeTask = ref('resume_generate')
const result = ref('')
const loading = ref(false)
const exporting = ref(false)
const historyLoading = ref(false)
const history = ref([])
const apiSource = ref('free')
const photoInput = ref(null)
const photoDataUrl = ref('')
const authStorageKey = 'resume_user_v4'
const locale = ref(localStorage.getItem('resume_locale') || 'zh')
const currentUser = ref(JSON.parse(localStorage.getItem(authStorageKey) || 'null'))
const sendingCode = ref(false)
const loggingIn = ref(false)
const emailForm = reactive({
  email: '',
  code: '',
  devCode: ''
})
const qrProviders = ['wechat', 'alipay']
const selectedQrProvider = ref('wechat')
const qrMode = ref(false)
const qrImage = ref('')
const qrSession = ref(null)
let qrPollTimer = null

const candidateName = computed(() => forms.resume_generate.name || 'Candidate')
const languageToggleLabel = computed(() => (locale.value === 'zh' ? 'English' : '中文'))
const sourceTagType = computed(() => {
  if (apiSource.value === 'openai') return 'success'
  if (apiSource.value === 'ollama') return 'warning'
  return 'info'
})
const sourceLabel = computed(() => {
  const labels = {
    openai: t('openaiActive'),
    ollama: t('localModelActive'),
    free: t('freeLocalMode'),
    mock: t('freeLocalMode')
  }
  return labels[apiSource.value] || t('freeLocalMode')
})
const resumeScore = computed(() => {
  let score = 28
  if (forms.resume_generate.name) score += 8
  if (forms.resume_generate.email) score += 8
  if (forms.resume_generate.projects.length > 40) score += 18
  if (forms.resume_generate.skills.length > 20) score += 14
  if (photoDataUrl.value) score += 7
  if (result.value) score += 17
  return Math.min(score, 100)
})
const renderedResult = computed(() => markdownToHtml(result.value))
const activeVisualStyle = computed(() => forms.resume_optimize.style || forms.resume_beautify.style || 'modern')
const previewStyleClass = computed(() => `resume-style-${activeVisualStyle.value}`)
const styleLabel = computed(() => {
  const labels = {
    modern: t('modern'),
    executive: t('executive'),
    'compact-ats': t('compactAts')
  }
  return labels[activeVisualStyle.value] || t('modern')
})
const styleDescriptor = computed(() => {
  const descriptions = {
    modern: t('styleModernDescription'),
    executive: t('styleExecutiveDescription'),
    'compact-ats': t('styleCompactDescription')
  }
  return descriptions[activeVisualStyle.value] || descriptions.modern
})

const taskOptions = computed(() => [
  { label: t('taskGenerate'), value: 'resume_generate' },
  { label: t('taskOptimize'), value: 'resume_optimize' },
  { label: t('taskInterview'), value: 'interview_questions' }
])

const taskMeta = computed(() => ({
  resume_generate: {
    title: t('resumeGenerator'),
    subtitle: t('resumeGeneratorSubtitle'),
    icon: DocumentChecked
  },
  resume_optimize: {
    title: t('resumeOptimizer'),
    subtitle: t('resumeOptimizerSubtitle'),
    icon: MagicStick
  },
  interview_questions: {
    title: t('interviewCoach'),
    subtitle: t('interviewCoachSubtitle'),
    icon: UserFilled
  }
}))

function t(key) {
  return messages[locale.value]?.[key] || messages.en[key] || key
}

function toggleLanguage() {
  locale.value = locale.value === 'zh' ? 'en' : 'zh'
  localStorage.setItem('resume_locale', locale.value)
}

function saveUser(user) {
  currentUser.value = user
  localStorage.setItem(authStorageKey, JSON.stringify(user))
  ElMessage.success(t('loginSuccess'))
}

async function sendCode() {
  if (!emailForm.email) {
    ElMessage.warning(t('enterEmail'))
    return
  }
  sendingCode.value = true
  try {
    const response = await requestEmailCode(emailForm.email)
    emailForm.devCode = response.dev_code
    emailForm.code = response.dev_code
    ElMessage.success(t('codeSent'))
  } catch {
    ElMessage.error(t('codeRequestFailed'))
  } finally {
    sendingCode.value = false
  }
}

async function loginWithEmail() {
  if (!emailForm.email) {
    ElMessage.warning(t('enterEmail'))
    return
  }
  if (!emailForm.code) {
    ElMessage.warning(t('enterCode'))
    return
  }
  loggingIn.value = true
  try {
    saveUser(await verifyEmailCode(emailForm.email, emailForm.code))
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || t('loginFailed'))
  } finally {
    loggingIn.value = false
  }
}

function logout() {
  currentUser.value = null
  localStorage.removeItem(authStorageKey)
  closeQrLogin()
}

function openQrLogin(provider) {
  selectedQrProvider.value = provider
  qrMode.value = true
  startQrSession(provider)
}

function closeQrLogin() {
  qrMode.value = false
  qrImage.value = ''
  qrSession.value = null
  stopQrPolling()
}

async function startQrSession(provider) {
  stopQrPolling()
  if (currentUser.value || !qrMode.value) return
  qrImage.value = ''
  try {
    qrSession.value = await createQrSession(provider)
    qrImage.value = await QRCode.toDataURL(qrSession.value.qr_url, {
      margin: 1,
      width: 220,
      color: {
        dark: '#111827',
        light: '#ffffff'
      }
    })
    qrPollTimer = window.setInterval(pollQrSession, 1800)
  } catch {
    ElMessage.error(t('qrCodeFailed'))
  }
}

async function pollQrSession() {
  if (!qrSession.value || currentUser.value) return
  try {
    const session = await getQrSession(qrSession.value.session_id)
    if (session.status === 'confirmed' && session.user) {
      stopQrPolling()
      saveUser(session.user)
    }
    if (session.status === 'expired') {
      startQrSession(selectedQrProvider.value)
    }
  } catch {
    stopQrPolling()
  }
}

function stopQrPolling() {
  if (qrPollTimer) {
    window.clearInterval(qrPollTimer)
    qrPollTimer = null
  }
}

async function submit() {
  loading.value = true
  try {
    const payload = { ...forms[activeTask.value] }
    let requestTask = activeTask.value
    if (activeTask.value === 'resume_generate') {
      payload.photo_data_url = photoDataUrl.value
    }
    if (activeTask.value === 'resume_optimize') {
      requestTask = 'resume_beautify'
      payload.photo_included = Boolean(photoDataUrl.value)
    }
    const response = await generateContent(requestTask, payload)
    result.value = response.content
    apiSource.value = response.source
    forms.resume_optimize.resume_text = response.content
    forms.resume_optimize.target_role = forms.resume_generate.target_role || forms.resume_optimize.target_role
    await loadHistory()
    ElMessage.success(t('generatedSuccessfully'))
  } catch (error) {
    const detail = error.response?.data?.detail
    ElMessage.error(Array.isArray(detail) ? detail[0]?.msg : detail || t('generationFailed'))
  } finally {
    loading.value = false
  }
}

function resetForm() {
  Object.assign(forms[activeTask.value], cloneDefaults()[activeTask.value])
}

function prepareBeautify() {
  forms.resume_optimize.resume_text = result.value
  forms.resume_optimize.target_role = forms.resume_generate.target_role || forms.resume_optimize.target_role
  activeTask.value = 'resume_optimize'
}

async function copyResult() {
  await navigator.clipboard.writeText(result.value)
  ElMessage.success(t('copied'))
}

async function downloadResult(format) {
  exporting.value = true
  try {
    const { blob, filename } = await exportDocument({
      content: result.value,
      format,
      file_name: `${candidateName.value || 'resume'}-${activeTask.value}`,
      candidate_name: candidateName.value,
      photo_data_url: photoDataUrl.value,
      style: activeVisualStyle.value
    })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(url)
    ElMessage.success(`${t('downloaded')} ${filename}`)
  } catch {
    ElMessage.error(t('exportFailed'))
  } finally {
    exporting.value = false
  }
}

function handlePhotoUpload(event) {
  const file = event.target.files?.[0]
  if (!file) return
  if (!file.type.startsWith('image/')) {
    ElMessage.error(t('uploadImageOnly'))
    return
  }
  if (file.size > 1.2 * 1024 * 1024) {
    ElMessage.error(t('imageTooLarge'))
    return
  }
  const reader = new FileReader()
  reader.onload = () => {
    photoDataUrl.value = String(reader.result)
  }
  reader.readAsDataURL(file)
}

async function loadHistory() {
  historyLoading.value = true
  try {
    history.value = await getHistory()
  } catch {
    history.value = []
  } finally {
    historyLoading.value = false
  }
}

function useHistory(row) {
  result.value = row.content
  activeTask.value = row.task_type === 'resume_beautify' ? 'resume_optimize' : row.task_type
}

function beautifyHistory(row) {
  result.value = row.content
  forms.resume_optimize.resume_text = row.content
  activeTask.value = 'resume_optimize'
}

async function removeHistory(id) {
  await deleteHistoryRecord(id)
  await loadHistory()
  ElMessage.success(t('deleted'))
}

function formatTaskType(taskType) {
  if (taskType === 'resume_beautify') return t('taskOptimize')
  if (taskType === 'cover_letter') return locale.value === 'zh' ? '旧任务' : 'Legacy task'
  return taskOptions.value.find((item) => item.value === taskType)?.label || taskType
}

function formatDate(value) {
  return new Intl.DateTimeFormat(undefined, {
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(value))
}

function markdownToHtml(markdown) {
  const escaped = markdown
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  return escaped
    .split('\n')
    .map((line) => {
      if (line.startsWith('# ')) return `<h1>${line.slice(2)}</h1>`
      if (line.startsWith('## ')) return `<h2>${line.slice(3)}</h2>`
      if (line.startsWith('- ')) return `<p class="bullet">• ${line.slice(2)}</p>`
      if (!line.trim()) return '<br />'
      return `<p>${line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')}</p>`
    })
    .join('')
}

watch(selectedQrProvider, (provider) => {
  if (qrMode.value) {
    startQrSession(provider)
  }
})

onMounted(() => {
  loadHistory()
})

onUnmounted(stopQrPolling)
</script>
