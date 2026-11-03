// Wix backend web module (backend/satsangProgress.web.js). Serves the My Course Dashboard.
// myCourses(): the courses the signed-in member has joined (with sections and lessons) and the ids of the steps they completed.
import { Permissions, webMethod } from 'wix-web-module';
import { currentMember } from 'wix-members-backend';
import { auth } from '@wix/essentials';
import { participants, resolvedSteps, programs, sections, steps } from '@wix/online-programs';

const CACHE = {};

// Courses always shown on the dashboard, whether or not the member has joined them (for now):
// Advanced Mind, Parents, Beginners (conversational) Mind.
const FEATURED = [
  'd6827644-429a-40fb-9c0d-1cf1d5a5a3d2',
  '7f5ad78b-461b-4c95-b070-4770e7d2e7eb',
  'e40d25ac-688f-409d-9bef-a028d126d7f6'
];

async function all(res) {
  const out = res.items.slice();
  while (res.hasNext()) { res = await res.next(); out.push(...res.items); }
  return out;
}

async function outline(pid) {
  const c = CACHE[pid];
  if (c && Date.now() - c.t < 600000) return c.v;
  const qp = auth.elevate(programs.queryPrograms);
  const p = (await qp().eq('_id', pid).limit(1).find()).items[0];
  const qs = auth.elevate(sections.querySections);
  const secs = (await qs().eq('programId', pid).limit(100).find()).items.filter(s => s.state === 'PUBLISHED');
  secs.sort((a, b) => a.ordering - b.ordering);
  const qt = auth.elevate(steps.querySteps);
  const sec = await Promise.all(secs.map(async s => {
    const st = (await qt().eq('sectionId', s._id).ascending('ordering').limit(100).find()).items;
    return { title: s.description && s.description.title, steps: st.map(x => [x._id, x.description && x.description.title, x.stepType]) };
  }));
  const v = { id: pid, title: p && p.description && p.description.title, slug: (p && p.seo && p.seo.slug) || pid, sections: sec };
  CACHE[pid] = { t: Date.now(), v };
  return v;
}

async function core() {
  const member = await currentMember.getMember();
  if (!member) return null;
  const qpar = auth.elevate(participants.queryParticipants);
  const mine = (await qpar().eq('memberId', member._id).limit(100).find()).items;
  const qres = auth.elevate(resolvedSteps.queryResolvedSteps);
  const completed = [];
  for (const me of mine) {
    const rows = await all(await qres().eq('participantId', me._id).limit(100).find());
    rows.filter(r => r.status === 'COMPLETED').forEach(r => completed.push(r.programStepId));
  }
  const ids = [...new Set([...mine.map(m => m.programId), ...FEATURED])];
  const courses = (await Promise.all(ids.map(id => outline(id).catch(() => null)))).filter(Boolean);
  return { courses, completed };
}

export const myCourses = webMethod(Permissions.Anyone, async () => core());

// older callers: just the completed step ids
export const myCompletedSteps = webMethod(Permissions.Anyone, async () => {
  const r = await core();
  return r ? r.completed : [];
});
