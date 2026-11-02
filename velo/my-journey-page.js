// Page code for the "My Journey" page on vedanta.nz (URL: /my-journey)
// The page holds one HTML element (Embed > Embed a site) with the ID: journeyFrame
// set to: https://ramakrishna-vedanta-centre-nz.github.io/satsangs/my-journey/
// Sends the signed-in member's own quiz results to the page for display.

import wixData from 'wix-data';
import { currentMember } from 'wix-members-frontend';
import { myCompletedSteps } from 'backend/satsangProgress.web'; // optional: lessons the member has marked complete

$w.onReady(async function () {
  const member = await currentMember.getMember({ fieldsets: ['FULL'] });
  let sent = false;

  $w('#journeyFrame').onMessage(async (event) => {
    if (!event.data || event.data.type !== 'ready' || sent) return;
    sent = true;
    if (!member) { $w('#journeyFrame').postMessage({ type: 'notMember' }); return; }
    const res = await wixData.query('QuizResults')
      .eq('_owner', member._id)
      .descending('_createdDate')
      .limit(1000)
      .find();
    let completedSteps;
    try { completedSteps = await myCompletedSteps(); } catch (err) { console.error(err); } // if this fails the dashboard still works from quiz results
    const cd = member.contactDetails || {};
    const name = cd.firstName || (member.profile && member.profile.nickname) || '';
    $w('#journeyFrame').postMessage({
      type: 'journey',
      name: name,
      completedSteps: completedSteps,
      results: res.items.map(r => ({
        code: r.title,
        title: r.quizTitle,
        programme: r.programme,
        score: r.score,
        maxScore: r.maxScore,
        percent: r.percent,
        date: (r.completedAt || r._createdDate)
      }))
    });
  });
});
