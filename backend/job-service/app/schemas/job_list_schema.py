from pydantic import BaseModel

class JobListResponse(BaseModel):
    result: str
    data: dict

    @classmethod
    def create(cls, result, job_data, page, size, total):
        return JobListResponse(
            result=result,
            data={
                "jobs": job_data,
                "page": page,
                "size": size,
                "total": total,
            }
        )

