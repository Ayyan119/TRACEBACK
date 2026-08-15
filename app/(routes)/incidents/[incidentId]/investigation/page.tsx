import { redirect } from 'next/navigation';

export default function InvestigationRedirect({ params }: { params: { incidentId: string } }) {
  redirect(`/projects/shopflow/incidents/${params.incidentId}/investigation`);
}
