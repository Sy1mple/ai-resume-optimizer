<template>
  <main class="app-shell">
    <section class="topbar">
      <div>
        <p class="eyebrow">AI Resume Optimizer</p>
        <h1>Job application workspace</h1>
      </div>
      <el-tag :type="apiSource === 'openai' ? 'success' : 'info'" effect="light">
        {{ apiSource === 'openai' ? 'OpenAI active' : 'Demo mode' }}
      </el-tag>
    </section>

    <section class="workspace">
      <div class="task-panel">
        <el-tabs v-model="activeTask" class="task-tabs">
          <el-tab-pane label="Resume" name="resume_generate">
            <el-form label-position="top">
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
            </el-form>
          </el-tab-pane>

          <el-tab-pane label="Optimize" name="resume_optimize">
            <el-form label-position="top">
              <el-form-item label="Target role">
                <el-input v-model="forms.resume_optimize.target_role" placeholder="Data Analyst" />
              </el-form-item>
              <el-form-item label="Resume text">
                <el-input v-model="forms.resume_optimize.resume_text" type="textarea" :rows="12" />
              </el-form-item>
            </el-form>
          </el-tab-pane>

          <el-tab-pane label="Cover Letter" name="cover_letter">
            <el-form label-position="top">
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
            </el-form>
          </el-tab-pane>

          <el-tab-pane label="Interview" name="interview_questions">
            <el-form label-position="top">
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
            </el-form>
          </el-tab-pane>
        </el-tabs>

        <div class="actions">
          <el-button :icon="RefreshLeft" @click="resetForm">Reset</el-button>
          <el-button type="primary" :icon="MagicStick" :loading="loading" @click="submit">
            Generate
          </el-button>
        </div>
      </div>

      <aside class="result-panel">
        <div class="panel-header">
          <div>
            <p class="eyebrow">Result</p>
            <h2>{{ taskLabels[activeTask] }}</h2>
          </div>
          <el-button :icon="CopyDocument" circle :disabled="!result" @click="copyResult" />
        </div>
        <pre v-if="result" class="result-output">{{ result }}</pre>
        <el-empty v-else description="Generated content appears here." />
      </aside>
    </section>

    <section class="history-section">
      <div class="panel-header">
        <div>
          <p class="eyebrow">History</p>
          <h2>Recent generations</h2>
        </div>
        <el-button :icon="Refresh" circle :loading="historyLoading" @click="loadHistory" />
      </div>
      <el-table :data="history" class="history-table" empty-text="No history yet">
        <el-table-column prop="task_type" label="Task" min-width="160" />
        <el-table-column label="Preview" min-width="320">
          <template #default="{ row }">
            <span class="preview-text">{{ row.content }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="Created" min-width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="140" fixed="right">
          <template #default="{ row }">
            <el-button :icon="View" circle @click="result = row.content" />
            <el-button :icon="Delete" circle type="danger" @click="removeHistory(row.id)" />
          </template>
        </el-table-column>
      </el-table>
    </section>
  </main>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { CopyDocument, Delete, MagicStick, Refresh, RefreshLeft, View } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { deleteHistoryRecord, generateContent, getHistory } from './api'

const taskLabels = {
  resume_generate: 'Resume generation',
  resume_optimize: 'Resume optimization',
  cover_letter: 'Cover letter',
  interview_questions: 'Interview assistant'
}

const defaultForms = {
  resume_generate: {
    name: 'Alex Chen',
    email: 'alex@example.com',
    phone: '+1 555 0100',
    education: 'B.S. in Computer Science, 2026. Coursework: data structures, databases, software engineering.',
    projects: 'Campus job board: built Vue pages, FastAPI endpoints, and PostgreSQL schema for job posts and applications.',
    skills: 'Vue, JavaScript, Python, FastAPI, SQL, Git',
    target_role: 'Frontend Developer'
  },
  resume_optimize: {
    target_role: 'Frontend Developer',
    resume_text: 'I made a website for students to find jobs. I used Vue and Python. I worked with classmates and fixed bugs.'
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
const historyLoading = ref(false)
const history = ref([])
const apiSource = ref('mock')

async function submit() {
  loading.value = true
  try {
    const response = await generateContent(activeTask.value, forms[activeTask.value])
    result.value = response.content
    apiSource.value = response.source
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

async function copyResult() {
  await navigator.clipboard.writeText(result.value)
  ElMessage.success('Copied')
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

onMounted(loadHistory)
</script>
