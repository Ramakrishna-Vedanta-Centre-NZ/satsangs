// Page code for the "Satsang Quiz" page on vedanta.nz (URL: /satsang-quiz)
// The page holds one HTML element (Embed > Embed a site) with the ID: quizFrame
// Opens the quiz chosen in the link, e.g. www.vedanta.nz/satsang-quiz?q=SAT-001
// and saves each completed quiz to the CMS collection "Quiz Results".

import wixData from 'wix-data';
import { currentMember } from 'wix-members-frontend';
import wixLocationFrontend from 'wix-location-frontend';

const BASE = 'https://ramakrishna-vedanta-centre-nz.github.io/satsangs/';

$w.onReady(async function () {
  const code = String(wixLocationFrontend.query.q || 'SAT-001').toUpperCase().replace(/[^A-Z0-9-]/g, '');
  $w('#quizFrame').src = BASE + code + '/quiz/?embed=1';

  const member = await currentMember.getMember({ fieldsets: ['FULL'] });

  $w('#quizFrame').onMessage(async (event) => {
    const d = event.data;
    if (!d || d.type !== 'quizResult') return;
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
    } catch (err) {
      console.error(err);
      $w('#quizFrame').postMessage({ type: 'saveError' });
    }
  });
});
