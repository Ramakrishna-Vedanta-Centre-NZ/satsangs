// Page code for the "Quiz" page on vedanta.nz (URL: /quiz). Serves every quiz: satsangs and course lessons.
// The page holds one HTML element (Embed > Embed a site) with the ID: quizFrame
// Opens the quiz chosen in the link, e.g. www.vedanta.nz/quiz?q=SAT-001 (or ?q=MIND-L01 for a course lesson),
// keeps a member's unfinished answers in "Quiz Progress" so they can continue on any device,
// and saves each completed quiz to "Quiz Results".
import wixData from 'wix-data';
import { currentMember } from 'wix-members-frontend';
import wixLocationFrontend from 'wix-location-frontend';

const BASE = 'https://ramakrishna-vedanta-centre-nz.github.io/satsangs/';

$w.onReady(async function () {
  const code = String(wixLocationFrontend.query.q || 'SAT-001').toUpperCase().replace(/[^A-Z0-9-]/g, '');
  $w('#quizFrame').src = BASE + code + '/quiz/?embed=1';

  const member = await currentMember.getMember({ fieldsets: ['FULL'] });
  const progressId = member ? code + '-' + member._id : null;

  $w('#quizFrame').onMessage(async (event) => {
    const d = event.data || {};

    // The quiz has loaded: send back any unfinished answers saved for this member
    if (d.type === 'ready') {
      let state = null;
      if (progressId) {
        try {
          const item = await wixData.get('QuizProgress', progressId);
          if (item && item.state) state = JSON.parse(item.state);
        } catch (err) { console.error(err); }
      }
      $w('#quizFrame').postMessage({ type: 'resume', state: state });
      return;
    }

    // An answer was given: keep the member's progress (or clear it when they start again)
    if (d.type === 'progress') {
      if (!progressId || d.code !== code) return;
      try {
        if (d.state) await wixData.save('QuizProgress', { _id: progressId, title: code, state: JSON.stringify(d.state) });
        else await wixData.remove('QuizProgress', progressId);
      } catch (err) { console.error(err); }
      return;
    }

    // The quiz is finished: save the result
    if (d.type !== 'quizResult') return;
    if (!member) { $w('#quizFrame').postMessage({ type: 'notMember' }); return; }
    const cd = member.contactDetails || {};
    const name = [cd.firstName, cd.lastName].filter(Boolean).join(' ') || (member.profile && member.profile.nickname) || '';
    try {
      await wixData.insert('QuizResults', {
        title: d.code,
        quizTitle: d.title,
        programme: d.programme,
        memberName: name,
        memberEmail: member.loginEmail || '',
        score: d.score,
        maxScore: d.maxScore,
        percent: d.percent,
        questionsCorrect: d.questionsCorrect,
        questionCount: d.questionCount,
        answers: JSON.stringify(d.answers || []),
        completedAt: new Date()
      });
      $w('#quizFrame').postMessage({ type: 'saved' });
      wixData.remove('QuizProgress', progressId).catch(() => {});
    } catch (err) {
      console.error(err);
      $w('#quizFrame').postMessage({ type: 'saveError' });
    }
  });
});
