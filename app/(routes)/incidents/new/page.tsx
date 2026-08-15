import { redirect } from 'next/navigation';

export default function NewIncidentRedirect() {
  redirect('/projects/shopflow/incidents/new');
}
