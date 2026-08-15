import { redirect } from 'next/navigation';

export default function IncidentDetailRedirect({ params }: { params: { incidentId: string } }) {
  redirect(`/projects/shopflow/incidents/${params.incidentId}`);
}
