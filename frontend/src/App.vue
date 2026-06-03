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
          <span class="workspace-badge">{{ t('proWorkspace') }}</span>
        </div>
      </div>

      <section class="profile-card">
        <div class="account-row">
          <div class="account-avatar">{{ userInitial }}</div>
          <div>
            <p>{{ currentUser.display_name || t('candidateAccount') }}</p>
            <span>{{ currentUser.email || currentUser.provider }}</span>
          </div>
        </div>
        <div class="photo-row">
          <div class="photo-upload">
            <img v-if="photoDataUrl" :src="photoDataUrl" alt="Candidate portrait" />
            <UserFilled v-else class="photo-placeholder" />
            <input ref="photoInput" type="file" accept="image/*" @change="handlePhotoUpload" />
          </div>
          <div class="photo-actions">
            <el-button :icon="Upload" @click="photoInput?.click()">{{ t('uploadPhoto') }}</el-button>
            <el-button v-if="photoDataUrl" :icon="Delete" text @click="photoDataUrl = ''">{{ t('remove') }}</el-button>
          </div>
        </div>
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
        <p class="nav-label">{{ t('navWorkflow') }}</p>
        <button
          v-for="item in sideNavItems"
          :key="item.value"
          :class="{ active: activeTask === item.value }"
          @click="activeTask = item.value"
        >
          <component :is="item.icon" />
          <span>
            <b>{{ item.label }}</b>
            <small>{{ item.subtitle }}</small>
          </span>
          <i>{{ item.metric }}</i>
        </button>
        <p class="nav-label">{{ t('navAssets') }}</p>
        <button class="secondary-nav" @click="openSidebarShortcut('export')">
          <Download />
          <span>
            <b>{{ t('export') }}</b>
            <small>PDF / DOCX / MD</small>
          </span>
        </button>
        <button class="secondary-nav" @click="openSidebarShortcut('history')">
          <Refresh />
          <span>
            <b>{{ t('history') }}</b>
            <small>{{ history.length }} {{ t('records') }}</small>
          </span>
        </button>
      </nav>

      <section class="sidebar-insight">
        <p class="eyebrow">{{ t('pipelineOverview') }}</p>
        <div class="insight-grid">
          <span>
            <b>{{ resumeScore }}%</b>
            {{ t('completion') }}
          </span>
          <span>
            <b>{{ selectedPlatforms.length }}</b>
            {{ t('channels') }}
          </span>
        </div>
      </section>
    </aside>

    <section class="main-workspace">
      <header class="topbar">
        <div>
          <p class="eyebrow">{{ t('resumeStudio') }}</p>
          <h2>{{ t('appSubtitle') }}</h2>
          <div class="topbar-pills">
            <span>{{ styleLabel }}</span>
            <span>{{ resumeScore }}%</span>
          </div>
        </div>
        <div class="topbar-actions">
          <el-button class="api-key-button" @click="apiDialogVisible = true">
            {{ openaiApiKey ? t('apiKeyConfigured') : t('paidApiShort') }}
          </el-button>
          <el-button @click="toggleLanguage">{{ languageToggleLabel }}</el-button>
          <el-button text @click="logout">{{ t('logout') }}</el-button>
        </div>
      </header>

      <el-dialog v-model="apiDialogVisible" :title="t('apiKeyTitle')" width="420px" class="api-key-dialog">
        <el-form label-position="top">
          <el-form-item :label="t('apiKeyLabel')">
            <el-input
              v-model="apiKeyDraft"
              type="password"
              show-password
              :placeholder="t('apiKeyPlaceholder')"
            />
          </el-form-item>
        </el-form>
        <p class="api-key-note">{{ t('apiKeyHelp') }}</p>
        <template #footer>
          <el-button @click="clearApiKey">{{ t('clearApiKey') }}</el-button>
          <el-button type="primary" @click="saveApiKey">{{ t('saveApiKey') }}</el-button>
        </template>
      </el-dialog>

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
                  <el-form-item :label="t('visualStyle')">
                    <el-select v-model="forms.resume_generate.style">
                      <el-option :label="t('modern')" value="modern" />
                      <el-option :label="t('executive')" value="executive" />
                      <el-option :label="t('compactAts')" value="compact-ats" />
                    </el-select>
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
                <el-form-item :label="t('projectIntro')">
                  <el-input v-model="forms.resume_generate.project_intro" type="textarea" :rows="3" :placeholder="t('projectIntroPlaceholder')" />
                </el-form-item>
                <el-form-item :label="t('projectArchitecture')">
                  <el-input v-model="forms.resume_generate.project_architecture" type="textarea" :rows="3" :placeholder="t('projectArchitecturePlaceholder')" />
                </el-form-item>
                <el-form-item :label="t('technicalArchitecture')">
                  <el-input v-model="forms.resume_generate.technical_architecture" type="textarea" :rows="3" :placeholder="t('technicalArchitecturePlaceholder')" />
                </el-form-item>
                <el-form-item :label="t('personalResponsibilities')">
                  <el-input v-model="forms.resume_generate.personal_responsibilities" type="textarea" :rows="4" :placeholder="t('personalResponsibilitiesPlaceholder')" />
                </el-form-item>
                <el-form-item :label="t('skills')">
                  <el-input v-model="forms.resume_generate.skills" type="textarea" :rows="3" />
                </el-form-item>
                <el-form-item :label="t('resumeContentToBeautify')">
                  <el-input v-model="forms.resume_generate.source_resume_text" type="textarea" :rows="5" :placeholder="t('sourceResumePlaceholder')" />
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

              <template v-if="activeTask === 'job_match'">
                <div class="grid-2">
                  <el-form-item :label="t('targetRole')">
                    <el-input v-model="forms.job_match.target_role" :placeholder="t('targetRolePlaceholder')" />
                  </el-form-item>
                  <el-form-item :label="t('targetCity')">
                    <el-input v-model="forms.job_match.city" :placeholder="t('targetCityPlaceholder')" />
                  </el-form-item>
                  <el-form-item :label="t('salaryRange')">
                    <el-input v-model="forms.job_match.salary_range" :placeholder="t('salaryPlaceholder')" />
                  </el-form-item>
                  <el-form-item :label="t('jobKeywords')">
                    <el-input v-model="forms.job_match.keywords" :placeholder="t('jobKeywordsPlaceholder')" />
                  </el-form-item>
                </div>
                <el-form-item :label="t('recruitingPlatforms')">
                  <el-checkbox-group v-model="forms.job_match.platforms" class="platform-checkboxes">
                    <el-checkbox-button
                      v-for="platform in platformOptions"
                      :key="platform.value"
                      :label="platform.value"
                    >
                      {{ platform.label }}
                    </el-checkbox-button>
                  </el-checkbox-group>
                </el-form-item>
                <el-form-item :label="t('resumeForMatching')">
                  <el-input
                    v-model="forms.job_match.resume_text"
                    type="textarea"
                    :rows="7"
                    :placeholder="t('resumeForMatchingPlaceholder')"
                  />
                </el-form-item>
                <div class="connector-note">
                  <Link />
                  <span>{{ t('connectorNote') }}</span>
                </div>
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

          <div v-if="activeTask === 'job_match'" class="job-match-board">
            <div class="match-summary">
              <div>
                <p class="eyebrow">{{ t('matchReadiness') }}</p>
                <strong>{{ jobMatchScore }}%</strong>
              </div>
              <span>{{ t('deliveryQueue') }} {{ appliedCount }}/{{ jobMatches.length }}</span>
            </div>
            <div class="job-card-list">
              <article v-for="job in jobMatches" :key="job.id" class="job-card">
                <div class="job-card-top">
                  <div>
                    <p>{{ platformLabel(job.platform) }}</p>
                    <h4>{{ job.title }}</h4>
                  </div>
                  <strong>{{ job.score }}%</strong>
                </div>
                <div class="job-meta-row">
                  <span>{{ job.company }}</span>
                  <span>{{ job.city }}</span>
                  <span>{{ job.salary }}</span>
                </div>
                <div class="job-tags">
                  <span v-for="tag in job.tags" :key="tag">{{ tag }}</span>
                </div>
                <p class="job-reason">{{ job.reason }}</p>
                <div class="job-actions">
                  <el-select v-model="applicationStatuses[job.id]" size="small">
                    <el-option :label="t('statusTodo')" value="todo" />
                    <el-option :label="t('statusOpened')" value="opened" />
                    <el-option :label="t('statusApplied')" value="applied" />
                    <el-option :label="t('statusFollowUp')" value="follow-up" />
                  </el-select>
                  <el-button type="primary" :icon="Promotion" @click="openJobPortal(job)">
                    {{ t('openDelivery') }}
                  </el-button>
                </div>
              </article>
            </div>
            <div v-if="result" class="match-report">
              <p class="eyebrow">{{ t('aiMatchReport') }}</p>
              <article v-html="renderedResult"></article>
            </div>
          </div>

          <div v-else-if="result" class="resume-preview" :class="previewStyleClass">
            <div class="preview-header">
              <img v-if="photoDataUrl" :src="photoDataUrl" alt="Candidate portrait" />
              <div>
                <span>{{ forms.resume_generate.target_role || t('targetRole') }}</span>
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

      <section id="history-section" class="history-section">
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
  Briefcase,
  CopyDocument,
  Delete,
  DocumentChecked,
  Download,
  Link,
  MagicStick,
  Promotion,
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
    proWorkspace: 'Pro workspace',
    candidateAccount: 'Candidate account',
    uploadPhoto: 'Upload photo',
    remove: 'Remove',
    resumeReadiness: 'Resume readiness',
    ready: 'Ready',
    draft: 'Draft',
    photo: 'Photo',
    included: 'Included',
    optional: 'Optional',
    export: 'Export',
    appSubtitle: 'Generate, polish, and export one high-quality resume workflow',
    paidApiShort: 'Paid API',
    apiKeyConfigured: 'API configured',
    apiKeyTitle: 'Use paid OpenAI API',
    apiKeyLabel: 'OpenAI API key',
    apiKeyPlaceholder: 'sk-...',
    apiKeyHelp: 'The key is kept in this browser session and sent only when generating content with paid API enabled.',
    saveApiKey: 'Save key',
    clearApiKey: 'Clear key',
    apiKeySaved: 'API key saved',
    apiKeyCleared: 'API key cleared',
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
    projectIntro: 'Project introduction',
    projectIntroPlaceholder: 'What the project does, users served, business scenario, and core value.',
    projectArchitecture: 'Project architecture',
    projectArchitecturePlaceholder: 'Frontend, backend, data flow, modules, services, and integration relationships.',
    technicalArchitecture: 'Technical architecture',
    technicalArchitecturePlaceholder: 'Frameworks, libraries, database, API design, deployment, and engineering choices.',
    personalResponsibilities: 'Personal responsibilities',
    personalResponsibilitiesPlaceholder: 'Your ownership, delivered modules, collaboration, optimization, and measurable outcomes.',
    skills: 'Skills',
    resumeText: 'Resume text',
    visualStyle: 'Visual style',
    modern: 'Modern',
    executive: 'Executive',
    compactAts: 'Compact ATS',
    resumeContentToBeautify: 'Existing resume draft',
    sourceResumePlaceholder: 'Optional: paste an existing resume draft here. If provided, Generate will optimize and style it directly.',
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
    taskGenerate: 'Generate & Optimize',
    taskOptimize: 'Optimize & Style',
    taskBeautify: 'Beautify',
    taskInterview: 'Interview',
    taskJobMatch: 'Job Match',
    resumeGenerator: 'Resume generator and optimizer',
    resumeGeneratorSubtitle: 'Create, rewrite, and style a recruiter-ready resume in one place.',
    jobMatchStudio: 'Recruiting match and delivery',
    jobMatchStudioSubtitle: 'Score job fit, build a delivery queue, and open compliant platform entries.',
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
    qrCodeFailed: 'QR code failed',
    targetCity: 'Target city',
    targetCityPlaceholder: 'Shanghai / Remote',
    salaryRange: 'Salary range',
    salaryPlaceholder: '20k-35k / month',
    jobKeywords: 'Search keywords',
    jobKeywordsPlaceholder: 'Vue, FastAPI, AI resume',
    recruitingPlatforms: 'Recruiting platforms',
    resumeForMatching: 'Resume for matching',
    resumeForMatchingPlaceholder: 'Paste the resume you want to deliver. The current generated resume can be reused here.',
    connectorNote: 'Platform connectors use official search or authorized API entry points. The demo creates safe delivery links and a trackable queue.',
    matchReadiness: 'Match readiness',
    deliveryQueue: 'Delivery queue',
    statusTodo: 'To review',
    statusOpened: 'Opened',
    statusApplied: 'Applied',
    statusFollowUp: 'Follow up',
    openDelivery: 'Open delivery',
    aiMatchReport: 'AI match report',
    navWorkflow: 'Workflow',
    navAssets: 'Assets',
    records: 'records',
    pipelineOverview: 'Pipeline overview',
    completion: 'Complete',
    channels: 'Channels',
    navGenerateSubtitle: 'Resume drafting',
    navMatchSubtitle: 'Job delivery',
    navInterviewSubtitle: 'Interview prep',
    noExportYet: 'Generate content before exporting'
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
    proWorkspace: '专业工作区',
    candidateAccount: '候选人账户',
    uploadPhoto: '上传照片',
    remove: '移除',
    resumeReadiness: '简历完成度',
    ready: '已就绪',
    draft: '草稿',
    photo: '照片',
    included: '已加入',
    optional: '可选',
    export: '导出',
    appSubtitle: '一站式生成、优化并导出高质量简历',
    paidApiShort: '付费 API',
    apiKeyConfigured: 'API 已配置',
    apiKeyTitle: '使用付费 OpenAI API',
    apiKeyLabel: 'OpenAI API Key',
    apiKeyPlaceholder: 'sk-...',
    apiKeyHelp: 'Key 只保存在当前浏览器会话中，只有生成内容时才会发送到本地后端调用付费 API。',
    saveApiKey: '保存 Key',
    clearApiKey: '清除 Key',
    apiKeySaved: 'API Key 已保存',
    apiKeyCleared: 'API Key 已清除',
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
    projectIntro: '项目介绍',
    projectIntroPlaceholder: '说明项目背景、服务对象、业务场景和核心价值。',
    projectArchitecture: '项目架构',
    projectArchitecturePlaceholder: '说明前端、后端、数据流、模块划分、服务关系和集成方式。',
    technicalArchitecture: '技术架构',
    technicalArchitecturePlaceholder: '说明框架、组件库、数据库、接口设计、部署方式和工程化选择。',
    personalResponsibilities: '个人职责',
    personalResponsibilitiesPlaceholder: '说明你负责的模块、交付内容、协作方式、优化结果和量化成果。',
    skills: '技能',
    resumeText: '简历文本',
    visualStyle: '视觉风格',
    modern: '现代风',
    executive: '商务风',
    compactAts: '紧凑 ATS',
    resumeContentToBeautify: '已有简历草稿',
    sourceResumePlaceholder: '可选：粘贴已有简历草稿；如果填写，点击生成会直接优化并美化这份内容。',
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
    taskGenerate: '生成优化',
    taskOptimize: '优化美化',
    taskBeautify: '美化',
    taskInterview: '面试',
    taskJobMatch: '岗位匹配',
    resumeGenerator: '简历生成优化',
    resumeGeneratorSubtitle: '在一个入口里完成生成、改写、强化和版式风格整理。',
    jobMatchStudio: '招聘匹配投放',
    jobMatchStudioSubtitle: '匹配岗位、生成投递队列，并打开合规的招聘平台入口。',
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
    qrCodeFailed: '二维码生成失败',
    targetCity: '目标城市',
    targetCityPlaceholder: '上海 / 远程',
    salaryRange: '期望薪资',
    salaryPlaceholder: '20k-35k / 月',
    jobKeywords: '搜索关键词',
    jobKeywordsPlaceholder: 'Vue、FastAPI、AI 简历',
    recruitingPlatforms: '招聘渠道',
    resumeForMatching: '用于匹配的简历',
    resumeForMatchingPlaceholder: '粘贴要投递的简历，也可以把当前生成的简历复用到这里。',
    connectorNote: '招聘网站连接器使用官方搜索入口或授权 API。当前版本生成安全投递链接和可追踪投递队列。',
    matchReadiness: '匹配准备度',
    deliveryQueue: '投递队列',
    statusTodo: '待筛选',
    statusOpened: '已打开',
    statusApplied: '已投递',
    statusFollowUp: '待跟进',
    openDelivery: '打开投递',
    aiMatchReport: 'AI 匹配报告',
    navWorkflow: '工作流',
    navAssets: '资产',
    records: '条记录',
    pipelineOverview: '流程概览',
    completion: '完成度',
    channels: '渠道',
    navGenerateSubtitle: '简历生成优化',
    navMatchSubtitle: '岗位匹配投放',
    navInterviewSubtitle: '面试题准备',
    noExportYet: '请先生成内容再导出'
  }
}

const initialLocale = localStorage.getItem('resume_locale') || 'zh'
const defaultFormPresets = {
  zh: {
    resume_generate: {
      name: '陈同学',
      email: 'chen@example.com',
      phone: '138 0000 0000',
      education: '计算机科学与技术本科，2026 届。主修课程：数据结构、数据库、软件工程、Web 开发。',
      projects: '校园招聘系统：负责 Vue 页面、FastAPI 接口和 SQL 数据表设计。',
      project_intro: '面向学生和企业的校园招聘系统，支持职位浏览、岗位发布、简历投递和申请进度管理。',
      project_architecture: '前端使用 Vue 构建页面与状态交互，后端通过 FastAPI 提供 REST API，数据库按用户、职位、投递记录等模块拆分。',
      technical_architecture: 'Vue 3、JavaScript、Element Plus、FastAPI、SQL 数据库、REST API、Git 协作流程。',
      personal_responsibilities: '负责简历页面和岗位页面开发、接口联调、核心数据表设计，并优化投递流程的可用性。',
      skills: 'Vue, JavaScript, Python, FastAPI, SQL, Git',
      target_role: '前端开发工程师',
      style: 'modern',
      source_resume_text: '',
      photo_data_url: ''
    },
    resume_beautify: {
      target_role: '前端开发工程师',
      style: 'modern',
      resume_text: '请先生成或粘贴简历内容，然后进行优化和排版。',
      photo_included: false
    },
    interview_questions: {
      job_title: '前端开发实习生',
      technical_direction: 'Vue 3、JavaScript、REST API、浏览器性能优化',
      experience_level: 'Entry level'
    },
    job_match: {
      target_role: '前端开发工程师',
      city: '上海',
      salary_range: '20k-35k / 月',
      platforms: ['boss', 'lagou', 'liepin'],
      keywords: 'Vue, JavaScript, FastAPI, AI 简历',
      resume_text: '具备 Vue、JavaScript、Python、FastAPI、SQL 和 Git 项目经验，曾完成校园招聘系统的职位发布、投递流程和接口联调。'
    }
  },
  en: {
    resume_generate: {
      name: 'Alex Chen',
      email: 'alex@example.com',
      phone: '+1 555 0100',
      education: 'B.S. in Computer Science, 2026. Coursework: data structures, databases, software engineering, and web development.',
      projects: 'Campus job board: built Vue pages, FastAPI endpoints, and PostgreSQL schema for job posts and applications.',
      project_intro: 'Campus job board for students and employers, covering job browsing, posting, resume submission, and application tracking.',
      project_architecture: 'Vue frontend communicates with FastAPI backend through REST APIs. Backend separates users, job posts, and application records into clear modules.',
      technical_architecture: 'Vue 3, JavaScript, Element Plus, FastAPI, SQL database, REST API, Git workflow.',
      personal_responsibilities: 'Built resume and job-post pages, implemented API integration, designed core SQL tables, and improved application flow usability.',
      skills: 'Vue, JavaScript, Python, FastAPI, SQL, Git',
      target_role: 'Frontend Developer',
      style: 'modern',
      source_resume_text: '',
      photo_data_url: ''
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
    },
    job_match: {
      target_role: 'Frontend Developer',
      city: 'Shanghai',
      salary_range: '20k-35k / month',
      platforms: ['boss', 'lagou', 'liepin'],
      keywords: 'Vue, JavaScript, FastAPI, AI resume',
      resume_text: 'Frontend developer with Vue, JavaScript, Python, FastAPI, SQL and Git experience. Built a campus job board with job posts, application flows, and API integrations.'
    }
  }
}

const cloneDefaults = (lang = initialLocale) => JSON.parse(JSON.stringify(defaultFormPresets[lang] || defaultFormPresets.zh))
const forms = reactive(cloneDefaults())
const activeTask = ref('resume_generate')
const result = ref('')
const loading = ref(false)
const exporting = ref(false)
const historyLoading = ref(false)
const history = ref([])
const openaiApiKey = ref(sessionStorage.getItem('resume_openai_api_key') || '')
const apiKeyDraft = ref(openaiApiKey.value)
const apiDialogVisible = ref(false)
const photoInput = ref(null)
const photoDataUrl = ref('')
const authStorageKey = 'resume_user_v4'
const locale = ref(initialLocale)
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
const applicationStatuses = reactive({})
let qrPollTimer = null

const candidateName = computed(() => forms.resume_generate.name || 'Candidate')
const userInitial = computed(() => {
  const name = currentUser.value?.display_name || currentUser.value?.email || 'AI'
  return String(name).slice(0, 1).toUpperCase()
})
const languageToggleLabel = computed(() => (locale.value === 'zh' ? 'English' : '中文'))
const resumeScore = computed(() => {
  let score = 28
  if (forms.resume_generate.name) score += 8
  if (forms.resume_generate.email) score += 8
  if (projectDraftContent().length > 40) score += 18
  if (forms.resume_generate.skills.length > 20) score += 14
  if (photoDataUrl.value) score += 7
  if (result.value) score += 17
  return Math.min(score, 100)
})
const renderedResult = computed(() => markdownToHtml(result.value))
const activeVisualStyle = computed(() => forms.resume_generate.style || forms.resume_beautify.style || 'modern')
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
const platformOptions = computed(() => [
  { label: 'Boss直聘', value: 'boss' },
  { label: '拉勾', value: 'lagou' },
  { label: '猎聘', value: 'liepin' },
  { label: '智联招聘', value: 'zhaopin' },
  { label: 'LinkedIn', value: 'linkedin' }
])
const selectedPlatforms = computed(() => forms.job_match.platforms.length ? forms.job_match.platforms : ['boss', 'lagou', 'liepin'])
const jobMatches = computed(() => {
  const role = forms.job_match.target_role || forms.resume_generate.target_role || 'Frontend Developer'
  const city = forms.job_match.city || 'Remote'
  const salary = forms.job_match.salary_range || 'Market rate'
  const resumeText = `${forms.job_match.resume_text} ${forms.resume_generate.skills} ${forms.resume_generate.projects}`.toLowerCase()
  const keywordHits = ['vue', 'javascript', 'python', 'fastapi', 'sql', 'api', 'ai']
    .filter((keyword) => resumeText.includes(keyword)).length
  const baseScore = Math.min(76 + keywordHits * 3 + (result.value ? 5 : 0), 96)
  return selectedPlatforms.value.slice(0, 5).map((platform, index) => ({
    id: `${platform}-${index}`,
    platform,
    title: index === 0 ? role : `${index === 1 ? 'Junior ' : ''}${role}${index === 2 ? ' Intern' : ''}`,
    company: ['Nova Talent Lab', 'BrightHire Cloud', 'Orbit Product Studio', 'FutureWorks AI', 'Northstar Tech'][index] || 'Hiring Team',
    city,
    salary,
    score: Math.max(baseScore - index * 5, 72),
    tags: buildJobTags(platform, index),
    reason: locale.value === 'zh'
      ? '技能关键词、项目经历和目标岗位方向匹配度较高，适合优先投递并定制开场说明。'
      : 'Skills, project evidence, and target direction align well. Prioritize this role and tailor the opening note.'
  }))
})
const jobMatchScore = computed(() => Math.round(jobMatches.value.reduce((sum, job) => sum + job.score, 0) / jobMatches.value.length))
const appliedCount = computed(() => Object.values(applicationStatuses).filter((status) => ['opened', 'applied', 'follow-up'].includes(status)).length)

const taskOptions = computed(() => [
  { label: t('taskGenerate'), value: 'resume_generate' },
  { label: t('taskJobMatch'), value: 'job_match' },
  { label: t('taskInterview'), value: 'interview_questions' }
])
const sideNavItems = computed(() => [
  {
    value: 'resume_generate',
    label: t('taskGenerate'),
    subtitle: t('navGenerateSubtitle'),
    metric: `${resumeScore.value}%`,
    icon: DocumentChecked
  },
  {
    value: 'job_match',
    label: t('taskJobMatch'),
    subtitle: t('navMatchSubtitle'),
    metric: `${jobMatchScore.value}%`,
    icon: Briefcase
  },
  {
    value: 'interview_questions',
    label: t('taskInterview'),
    subtitle: t('navInterviewSubtitle'),
    metric: forms.interview_questions.experience_level,
    icon: UserFilled
  }
])

const taskMeta = computed(() => ({
  resume_generate: {
    title: t('resumeGenerator'),
    subtitle: t('resumeGeneratorSubtitle'),
    icon: DocumentChecked
  },
  interview_questions: {
    title: t('interviewCoach'),
    subtitle: t('interviewCoachSubtitle'),
    icon: UserFilled
  },
  job_match: {
    title: t('jobMatchStudio'),
    subtitle: t('jobMatchStudioSubtitle'),
    icon: Briefcase
  }
}))

function t(key) {
  return messages[locale.value]?.[key] || messages.en[key] || key
}

function isUsingPreset(lang) {
  const preset = defaultFormPresets[lang] || defaultFormPresets.zh
  return Object.keys(preset).every((key) => JSON.stringify(forms[key]) === JSON.stringify(preset[key]))
}

function applyFormPreset(lang) {
  const preset = cloneDefaults(lang)
  Object.keys(preset).forEach((key) => {
    Object.assign(forms[key], preset[key])
  })
}

function platformLabel(platform) {
  return platformOptions.value.find((item) => item.value === platform)?.label || platform
}

function buildJobTags(platform, index) {
  const zhTags = {
    boss: ['即时沟通', '民企/初创', '移动端优先'],
    lagou: ['互联网', '产品技术', '成长型团队'],
    liepin: ['中高端', '猎头跟进', '稳定岗位'],
    zhaopin: ['校招社招', '覆盖广', 'HR 流程'],
    linkedin: ['国际化', '英文简历', '外企机会']
  }
  const enTags = {
    boss: ['Fast chat', 'Private firms', 'Mobile first'],
    lagou: ['Internet', 'Product tech', 'Growth team'],
    liepin: ['Mid-senior', 'Headhunter', 'Stable role'],
    zhaopin: ['Campus/social', 'Wide reach', 'HR process'],
    linkedin: ['Global', 'English resume', 'MNC roles']
  }
  const tags = locale.value === 'zh' ? zhTags : enTags
  return tags[platform] || ['ATS', 'Official entry', `Priority ${index + 1}`]
}

function platformSearchUrl(platform, job) {
  const query = encodeURIComponent(`${job.title} ${forms.job_match.city || ''}`.trim())
  const urls = {
    boss: `https://www.zhipin.com/web/geek/job?query=${query}`,
    lagou: `https://www.lagou.com/wn/jobs?kd=${query}`,
    liepin: `https://www.liepin.com/zhaopin/?key=${query}`,
    zhaopin: `https://sou.zhaopin.com/?kw=${query}`,
    linkedin: `https://www.linkedin.com/jobs/search/?keywords=${query}`
  }
  return urls[platform] || `https://www.google.com/search?q=${query}`
}

function openJobPortal(job) {
  applicationStatuses[job.id] = applicationStatuses[job.id] === 'applied' ? 'applied' : 'opened'
  window.open(platformSearchUrl(job.platform, job), '_blank', 'noopener,noreferrer')
}

function openSidebarShortcut(target) {
  if (target === 'history') {
    document.getElementById('history-section')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    return
  }
  if (!result.value) {
    ElMessage.warning(t('noExportYet'))
    return
  }
  downloadResult('pdf')
}

function toggleLanguage() {
  const previousLocale = locale.value
  const nextLocale = locale.value === 'zh' ? 'en' : 'zh'
  const shouldSwapPreset = isUsingPreset(previousLocale)
  locale.value = nextLocale
  localStorage.setItem('resume_locale', locale.value)
  if (shouldSwapPreset) {
    applyFormPreset(nextLocale)
  }
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

function projectDraftContent() {
  const sections = [
    [locale.value === 'zh' ? '项目介绍' : 'Project introduction', forms.resume_generate.project_intro],
    [locale.value === 'zh' ? '项目架构' : 'Project architecture', forms.resume_generate.project_architecture],
    [locale.value === 'zh' ? '技术架构' : 'Technical architecture', forms.resume_generate.technical_architecture],
    [locale.value === 'zh' ? '个人职责' : 'Personal responsibilities', forms.resume_generate.personal_responsibilities]
  ].filter(([, value]) => value?.trim())
  if (sections.length) {
    return sections.map(([title, value]) => `${title}:\n${value}`).join('\n\n')
  }
  return forms.resume_generate.projects
}

function resumeDraftLabels() {
  return locale.value === 'zh'
    ? {
        name: '姓名',
        email: '邮箱',
        phone: '电话',
        targetRole: '目标岗位',
        education: '教育经历',
        projects: '项目经历',
        skills: '专业技能'
      }
    : {
        name: 'Name',
        email: 'Email',
        phone: 'Phone',
        targetRole: 'Target role',
        education: 'Education',
        projects: 'Projects',
        skills: 'Skills'
      }
}

function buildResumeDraft() {
  if (forms.resume_generate.source_resume_text.trim()) {
    return forms.resume_generate.source_resume_text
  }
  const labels = resumeDraftLabels()
  return [
    `${labels.name}: ${forms.resume_generate.name}`,
    `${labels.email}: ${forms.resume_generate.email}`,
    `${labels.phone}: ${forms.resume_generate.phone}`,
    `${labels.targetRole}: ${forms.resume_generate.target_role}`,
    '',
    `${labels.education}:\n${forms.resume_generate.education}`,
    '',
    `${labels.projects}:\n${projectDraftContent()}`,
    '',
    `${labels.skills}:\n${forms.resume_generate.skills}`
  ].join('\n')
}

function buildJobMatchPayload() {
  return {
    ...forms.job_match,
    resume_text: forms.job_match.resume_text.trim() || buildResumeDraft()
  }
}

async function submit() {
  loading.value = true
  try {
    let requestTask = activeTask.value
    if (activeTask.value === 'resume_generate') {
      requestTask = 'resume_beautify'
    }
    const payload = activeTask.value === 'resume_generate'
      ? {
          target_role: forms.resume_generate.target_role,
          style: forms.resume_generate.style,
          resume_text: buildResumeDraft(),
          output_language: locale.value,
          photo_included: Boolean(photoDataUrl.value)
        }
      : activeTask.value === 'job_match'
        ? buildJobMatchPayload()
      : { ...forms[activeTask.value] }
    if (activeTask.value === 'interview_questions') {
      payload.experience_level = payload.experience_level || 'Entry level'
    }
    const provider = openaiApiKey.value ? 'openai' : 'free'
    const response = await generateContent(requestTask, payload, provider, openaiApiKey.value)
    result.value = response.content
    if (activeTask.value === 'resume_generate') {
      forms.resume_generate.source_resume_text = response.content
      forms.job_match.resume_text = response.content
    }
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
  Object.assign(forms[activeTask.value], cloneDefaults(locale.value)[activeTask.value])
}

function saveApiKey() {
  openaiApiKey.value = apiKeyDraft.value.trim()
  if (openaiApiKey.value) {
    sessionStorage.setItem('resume_openai_api_key', openaiApiKey.value)
    ElMessage.success(t('apiKeySaved'))
  }
  apiDialogVisible.value = false
}

function clearApiKey() {
  openaiApiKey.value = ''
  apiKeyDraft.value = ''
  sessionStorage.removeItem('resume_openai_api_key')
  apiDialogVisible.value = false
  ElMessage.success(t('apiKeyCleared'))
}

function prepareBeautify() {
  forms.resume_generate.source_resume_text = result.value
  activeTask.value = 'resume_generate'
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
  activeTask.value = ['resume_beautify', 'resume_optimize', 'cover_letter'].includes(row.task_type)
    ? 'resume_generate'
    : row.task_type
}

function beautifyHistory(row) {
  result.value = row.content
  forms.resume_generate.source_resume_text = row.content
  activeTask.value = 'resume_generate'
}

async function removeHistory(id) {
  await deleteHistoryRecord(id)
  await loadHistory()
  ElMessage.success(t('deleted'))
}

function formatTaskType(taskType) {
  if (['resume_beautify', 'resume_optimize'].includes(taskType)) return t('taskGenerate')
  if (taskType === 'cover_letter') return locale.value === 'zh' ? '旧任务' : 'Legacy task'
  if (taskType === 'job_match') return t('taskJobMatch')
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

watch(jobMatches, (matches) => {
  matches.forEach((job) => {
    if (!applicationStatuses[job.id]) {
      applicationStatuses[job.id] = 'todo'
    }
  })
}, { immediate: true })

onMounted(() => {
  loadHistory()
})

onUnmounted(stopQrPolling)
</script>
