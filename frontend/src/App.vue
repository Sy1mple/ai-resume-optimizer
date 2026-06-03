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
          <span>ATS</span>
          <b>{{ result ? t('ready') : t('draft') }}</b>
          <span>{{ t('photo') }}</span>
          <b>{{ photoDataUrl ? t('included') : t('optional') }}</b>
          <span>{{ t('export') }}</span>
          <b>PDF / DOCX / MD</b>
        </div>
      </section>
    </aside>

    <section class="main-workspace">
      <header class="topbar">
        <div>
          <p class="eyebrow">AI Resume Optimizer</p>
          <h2>{{ t('appSubtitle') }}</h2>
        </div>
        <div class="topbar-actions">
          <el-button @click="toggleLanguage">{{ languageToggleLabel }}</el-button>
          <el-tag :type="apiSource === 'openai' ? 'success' : 'info'" effect="light">
            {{ apiSource === 'openai' ? t('openaiActive') : t('demoMode') }}
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
                  <el-form-item label="Name">
                    <el-input v-model="forms.resume_generate.name" placeholder="Alex Chen" />
                  </el-form-item>
                  <el-form-item label="Target role">
                    <el-input v-model="forms.resume_generate.target_role" placeholder="Frontend Developer" />
                  </el-form-item>
                  <el-form-item label="Email">
                    <el-input v-model="forms.resume_generate.email" placeholder="alex@example.com" />
                  </el-form-item>
                  <el-form-item label="Phone">
                    <el-input v-model="forms.resume_generate.phone" placeholder="+1 555 0100" />
                  </el-form-item>
                </div>
                <el-form-item label="Education">
                  <el-input v-model="forms.resume_generate.education" type="textarea" :rows="3" />
                </el-form-item>
                <el-form-item label="Projects">
                  <el-input v-model="forms.resume_generate.projects" type="textarea" :rows="5" />
                </el-form-item>
                <el-form-item label="Skills">
                  <el-input v-model="forms.resume_generate.skills" type="textarea" :rows="3" />
                </el-form-item>
              </template>

              <template v-if="activeTask === 'resume_optimize'">
                <el-form-item label="Target role">
                  <el-input v-model="forms.resume_optimize.target_role" placeholder="Data Analyst" />
                </el-form-item>
                <el-form-item label="Resume text">
                  <el-input v-model="forms.resume_optimize.resume_text" type="textarea" :rows="12" />
                </el-form-item>
              </template>

              <template v-if="activeTask === 'resume_beautify'">
                <div class="grid-2">
                  <el-form-item label="Target role">
                    <el-input v-model="forms.resume_beautify.target_role" placeholder="Frontend Developer" />
                  </el-form-item>
                  <el-form-item label="Visual style">
                    <el-select v-model="forms.resume_beautify.style">
                      <el-option label="Modern" value="modern" />
                      <el-option label="Executive" value="executive" />
                      <el-option label="Compact ATS" value="compact-ats" />
                    </el-select>
                  </el-form-item>
                </div>
                <el-form-item label="Resume content to beautify">
                  <el-input v-model="forms.resume_beautify.resume_text" type="textarea" :rows="12" />
                </el-form-item>
              </template>

              <template v-if="activeTask === 'cover_letter'">
                <div class="grid-2">
                  <el-form-item label="Company">
                    <el-input v-model="forms.cover_letter.company_name" placeholder="Example Inc." />
                  </el-form-item>
                  <el-form-item label="Job title">
                    <el-input v-model="forms.cover_letter.job_title" placeholder="Product Intern" />
                  </el-form-item>
                </div>
                <el-form-item label="Personal experience">
                  <el-input v-model="forms.cover_letter.personal_experience" type="textarea" :rows="10" />
                </el-form-item>
              </template>

              <template v-if="activeTask === 'interview_questions'">
                <div class="grid-2">
                  <el-form-item label="Job title">
                    <el-input v-model="forms.interview_questions.job_title" placeholder="Backend Engineer" />
                  </el-form-item>
                  <el-form-item label="Experience level">
                    <el-select v-model="forms.interview_questions.experience_level">
                      <el-option label="Entry level" value="Entry level" />
                      <el-option label="Mid level" value="Mid level" />
                      <el-option label="Senior level" value="Senior level" />
                    </el-select>
                  </el-form-item>
                </div>
                <el-form-item label="Technical direction">
                  <el-input v-model="forms.interview_questions.technical_direction" placeholder="FastAPI, databases, REST APIs" />
                </el-form-item>
              </template>
            </el-form>
          </div>

          <div class="actions">
            <el-button :icon="RefreshLeft" @click="resetForm">Reset</el-button>
            <el-button :icon="StarFilled" :disabled="!result" @click="prepareBeautify">Beautify current</el-button>
            <el-button type="primary" :icon="MagicStick" :loading="loading" @click="submit">
              Generate
            </el-button>
          </div>
        </section>

        <aside class="result-panel">
          <div class="panel-header">
            <div>
              <p class="eyebrow">Live preview</p>
              <h3>{{ taskMeta[activeTask].title }}</h3>
            </div>
            <div class="result-tools">
              <el-button :icon="CopyDocument" circle :disabled="!result" @click="copyResult" />
              <el-dropdown trigger="click" :disabled="!result" @command="downloadResult">
                <el-button type="primary" :icon="Download" :loading="exporting">
                  Export
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="pdf">PDF</el-dropdown-item>
                    <el-dropdown-item command="docx">Word DOCX</el-dropdown-item>
                    <el-dropdown-item command="md">Markdown</el-dropdown-item>
                    <el-dropdown-item command="txt">Plain text</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>

          <div v-if="result" class="resume-preview" :class="previewStyleClass">
            <div class="preview-header">
              <img v-if="photoDataUrl" :src="photoDataUrl" alt="Candidate portrait" />
              <div>
                <span>{{ forms.resume_generate.target_role || forms.resume_beautify.target_role || 'Target role' }}</span>
                <strong>{{ candidateName }}</strong>
              </div>
            </div>
            <div class="style-strip">
              <span>{{ styleLabel }}</span>
              <i>{{ styleDescriptor }}</i>
            </div>
            <article v-html="renderedResult"></article>
          </div>
          <el-empty v-else description="Generate a resume, cover letter, or interview kit to preview it here." />
        </aside>
      </div>

      <section class="history-section">
        <div class="panel-header">
          <div>
            <p class="eyebrow">History</p>
            <h3>Recent generations</h3>
          </div>
          <el-button :icon="Refresh" circle :loading="historyLoading" @click="loadHistory" />
        </div>
        <el-table :data="history" class="history-table" empty-text="No history yet">
          <el-table-column prop="task_type" label="Task" min-width="160" />
          <el-table-column label="Preview" min-width="360">
            <template #default="{ row }">
              <span class="preview-text">{{ row.content }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="Created" min-width="180">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="Actions" width="168" fixed="right">
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
  Message,
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
    appSubtitle: 'Build, polish, and export a complete application kit',
    openaiActive: 'OpenAI active',
    demoMode: 'Demo mode',
    logout: 'Log out',
    codeSent: 'Verification code generated',
    loginSuccess: 'Signed in',
    enterEmail: 'Please enter your email',
    enterCode: 'Please enter the verification code'
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
    appSubtitle: '生成、优化并导出完整求职材料',
    openaiActive: 'OpenAI 已启用',
    demoMode: '演示模式',
    logout: '退出',
    codeSent: '验证码已生成',
    loginSuccess: '登录成功',
    enterEmail: '请输入邮箱',
    enterCode: '请输入验证码'
  }
}

const taskOptions = [
  { label: 'Generate', value: 'resume_generate' },
  { label: 'Optimize', value: 'resume_optimize' },
  { label: 'Beautify', value: 'resume_beautify' },
  { label: 'Letter', value: 'cover_letter' },
  { label: 'Interview', value: 'interview_questions' }
]

const taskMeta = {
  resume_generate: {
    title: 'Resume generator',
    subtitle: 'Create a recruiter-ready resume from structured profile details.',
    icon: DocumentChecked
  },
  resume_optimize: {
    title: 'Resume optimizer',
    subtitle: 'Rewrite rough resume text into stronger professional bullet points.',
    icon: MagicStick
  },
  resume_beautify: {
    title: 'One-click beautifier',
    subtitle: 'Turn the current draft into a polished, formatted resume layout.',
    icon: StarFilled
  },
  cover_letter: {
    title: 'Cover letter',
    subtitle: 'Generate a tailored letter for a company and role.',
    icon: Message
  },
  interview_questions: {
    title: 'Interview coach',
    subtitle: 'Prepare technical and behavioral questions with reference answers.',
    icon: UserFilled
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
    resume_text: 'I made a website for students to find jobs. I used Vue and Python. I worked with classmates and fixed bugs.'
  },
  resume_beautify: {
    target_role: 'Frontend Developer',
    style: 'modern',
    resume_text: 'Paste or generate a resume first, then use this tool to make it cleaner and more polished.',
    photo_included: false
  },
  cover_letter: {
    company_name: 'Example Inc.',
    job_title: 'Frontend Developer Intern',
    personal_experience: 'I built responsive Vue interfaces, integrated REST APIs, and improved usability based on peer feedback.'
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
const apiSource = ref('mock')
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
const activeVisualStyle = computed(() => forms.resume_beautify.style || 'modern')
const previewStyleClass = computed(() => `resume-style-${activeVisualStyle.value}`)
const styleLabel = computed(() => {
  const labels = {
    modern: 'Modern',
    executive: 'Executive',
    'compact-ats': 'Compact ATS'
  }
  return labels[activeVisualStyle.value] || 'Modern'
})
const styleDescriptor = computed(() => {
  const descriptions = {
    modern: 'Editorial spacing, color accents, portfolio-ready rhythm',
    executive: 'Formal typography, strong contrast, leadership framing',
    'compact-ats': 'Dense structure, monochrome hierarchy, scanner-friendly'
  }
  return descriptions[activeVisualStyle.value] || descriptions.modern
})

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
    ElMessage.error('Code request failed')
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
    ElMessage.error(error.response?.data?.detail || 'Login failed')
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
    ElMessage.error('QR code failed')
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
    if (activeTask.value === 'resume_generate') {
      payload.photo_data_url = photoDataUrl.value
    }
    if (activeTask.value === 'resume_beautify') {
      payload.photo_included = Boolean(photoDataUrl.value)
    }
    const response = await generateContent(activeTask.value, payload)
    result.value = response.content
    apiSource.value = response.source
    if (activeTask.value !== 'resume_beautify') {
      forms.resume_beautify.resume_text = response.content
      forms.resume_beautify.target_role = forms.resume_generate.target_role || forms.resume_optimize.target_role
    }
    await loadHistory()
    ElMessage.success('Generated successfully')
  } catch (error) {
    const detail = error.response?.data?.detail
    ElMessage.error(Array.isArray(detail) ? detail[0]?.msg : detail || 'Generation failed')
  } finally {
    loading.value = false
  }
}

function resetForm() {
  Object.assign(forms[activeTask.value], cloneDefaults()[activeTask.value])
}

function prepareBeautify() {
  forms.resume_beautify.resume_text = result.value
  forms.resume_beautify.target_role = forms.resume_generate.target_role || forms.resume_beautify.target_role
  forms.resume_beautify.photo_included = Boolean(photoDataUrl.value)
  activeTask.value = 'resume_beautify'
}

async function copyResult() {
  await navigator.clipboard.writeText(result.value)
  ElMessage.success('Copied')
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
    ElMessage.success(`Downloaded ${filename}`)
  } catch {
    ElMessage.error('Export failed')
  } finally {
    exporting.value = false
  }
}

function handlePhotoUpload(event) {
  const file = event.target.files?.[0]
  if (!file) return
  if (!file.type.startsWith('image/')) {
    ElMessage.error('Please upload an image file')
    return
  }
  if (file.size > 1.2 * 1024 * 1024) {
    ElMessage.error('Image must be smaller than 1.2 MB')
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
  activeTask.value = row.task_type
}

function beautifyHistory(row) {
  result.value = row.content
  forms.resume_beautify.resume_text = row.content
  activeTask.value = 'resume_beautify'
}

async function removeHistory(id) {
  await deleteHistoryRecord(id)
  await loadHistory()
  ElMessage.success('Deleted')
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
