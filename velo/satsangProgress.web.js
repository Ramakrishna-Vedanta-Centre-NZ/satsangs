// Backend web module for vedanta.nz (Velo > Backend > "satsangProgress.web.js").
// Returns the ids of the Satsang Study lessons that the signed-in member has marked complete.
// Needs the npm package @wix/online-programs (Velo sidebar > Packages) and @wix/essentials.
// DRAFT: written from the Wix docs and not yet run on the site. Test it once with the owner's account (see README note).
import { Permissions, webMethod } from 'wix-web-module';
import { currentMember } from 'wix-members-backend';
import { auth } from '@wix/essentials';
import { participants, resolvedSteps } from '@wix/online-programs';

const PROGRAM_ID = 'eb9c2b62-87b4-4e2e-aab6-19043659ded5'; // Satsang Study

export const myCompletedSteps = webMethod(Permissions.Anyone, async () => {
  const member = await currentMember.getMember();
  if (!member) return [];
  const queryParticipants = auth.elevate(participants.queryParticipants);
  const found = await queryParticipants().eq('programId', PROGRAM_ID).eq('memberId', member._id).limit(1).find();
  const me = found.items[0];
  if (!me) return [];
  const queryResolved = auth.elevate(resolvedSteps.queryResolvedSteps);
  const done = await queryResolved().eq('participantId', me._id).limit(100).find();
  return done.items.filter(r => r.status === 'COMPLETED').map(r => r.programStepId);
});
