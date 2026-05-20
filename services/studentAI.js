import {
  sendChat,
  getStudyPlan,
  getDailySchedule,
  getExamPrediction,
  getStudentDashboard,
  getAIContent
} from "./api";

/* =====================================================
   🧠 STUDENT AI BRAIN (HIGH LEVEL WRAPPERS)
===================================================== */

/* -------------------------
   🤖 ASK AI TUTOR
-------------------------- */
export async function askTutor(question) {
  if (!question) return null;

  return await sendChat(question);
}

/* -------------------------
   📚 GET STUDY PLAN
-------------------------- */
export async function generateStudyPlan(topics = []) {
  if (!topics.length) return null;

  return await getStudyPlan(topics);
}

/* -------------------------
   📅 DAILY SCHEDULE
-------------------------- */
export async function generateDailySchedule(topics = []) {
  if (!topics.length) return null;

  return await getDailySchedule(topics);
}

/* -------------------------
   📊 EXAM PREDICTION
-------------------------- */
export async function predictExam(topics = []) {
  if (!topics.length) return null;

  return await getExamPrediction(topics);
}

/* -------------------------
   📚 STUDENT DASHBOARD
-------------------------- */
export async function getDashboard() {
  return await getStudentDashboard();
}

/* -------------------------
   📄 AI NOTES FROM MATERIAL
-------------------------- */
export async function getNotes(materialId) {
  if (!materialId) return null;

  const res = await getAIContent(materialId);

  return res?.package || res;
}

/* =====================================================
   🧠 SMART COMBINED AI ACTION (POWER FEATURE)
===================================================== */
export async function fullLearningAnalysis(topics) {
  if (!topics?.length) return null;

  const [plan, schedule, exam] = await Promise.all([
    getStudyPlan(topics),
    getDailySchedule(topics),
    getExamPrediction(topics),
  ]);

  return {
    studyPlan: plan,
    schedule,
    examPrediction: exam,
  };
}