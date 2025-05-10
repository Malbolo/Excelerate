import { useEffect, useState } from 'react';

import { useParams } from 'react-router-dom';

import { JobResponse, useGetJobDetail } from '@/apis/jobManagement';

const JobEditPage = () => {
  const { jobId } = useParams();
  const getJobDetail = useGetJobDetail();
  const [jobDetail, setJobDetail] = useState<JobResponse | null>(null);

  useEffect(() => {
    const fetchJobDetail = async () => {
      if (!jobId) return;

      const data = await getJobDetail(jobId);
      setJobDetail(data);
    };

    fetchJobDetail();
  }, [jobId, getJobDetail]);

  if (!jobDetail) {
    return <div>Job not found</div>;
  }

  return (
    <div>
      <h1>{jobDetail.title}</h1>
    </div>
  );
};

export default JobEditPage;
