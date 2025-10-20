#############################################################################################
#  Imports
#############################################################################################
from Deadline.Events import DeadlineEventListener
from Deadline.Scripting import RepositoryUtils

import json
import requests
import sys

###############################################################
# Give Deadline an instance of this class so it can use it.
###############################################################
def GetDeadlineEventListener():
    return RenderTracker()

def CleanupDeadlineEventListener(eventListener):
    eventListener.Cleanup()

#############################################################################################
#  ZephyrTracker event listener class.
#############################################################################################
class RenderTracker (DeadlineEventListener):
    def __init__(self):
        self.OnJobSubmittedCallback += self.OnJobSubmitted
        self.OnJobStartedCallback += self.OnJobStarted
        self.OnJobFinishedCallback += self.OnJobFinished
        # self.onJobDeletedCallback += self.onJobDeleted
        self.OnJobRequeuedCallback += self.OnJobRequeued
        self.OnJobSuspendedCallback += self.OnJobSuspended
        self.OnJobResumedCallback += self.OnJobResumed
        self.OnJobFailedCallback += self.OnJobFailed
        self.OnJobErrorCallback += self.OnJobError
        
        if sys.version_info.major == 3:
            super().__init__()

    def Cleanup(self):
        del self.OnJobSubmittedCallback
        del self.OnJobStartedCallback
        del self.OnJobFinishedCallback
        # del self.OnJobDeletedCallback
        del self.OnJobRequeuedCallback
        del self.OnJobSuspendedCallback
        del self.OnJobResumedCallback
        del self.OnJobFailedCallback
        del self.OnJobErrorCallback

    def OnJobSubmitted(self, job):
        self.SendToAPI(job, 'Queued')

    def OnJobStarted(self, job):
        self.SendToAPI(job, 'Rendering')

    def OnJobFinished(self, job):
        self.SendToAPI(job, 'Completed')

    # def onJobDeleted(self, job):
    #     self.SendToAPI(job, 'Deleted')

    def OnJobRequeued(self, job):
        self.SendToAPI(job, 'Requeued')

    def OnJobSuspended(self, job):
        self.SendToAPI(job, 'Suspended')

    def OnJobResumed(self, job):
        self.SendToAPI(job, 'Resumed')

    def OnJobFailed(self, job):
        self.SendToAPI(job, 'Failed')

    def OnJobError(self, job):
        self.SendToAPI(job, 'Error')

    def JobDump(self, job):
      for attr in dir(job):
        try:
          val = getattr(job, attr)
          self.LogInfo(f"{attr}: {val}")
        except:
          pass

    def SendToAPI(self, job, status):
        # Get configuration values
        apiEndpoint = self.GetConfigEntryWithDefault("APIEndpoint", "")
        apiPort = self.GetConfigEntryWithDefault("APIPort", "3001")
        tenantId = self.GetConfigEntryWithDefault("TenantId", "")

        # Debug logging
        self.LogInfo(f"ZephyrTracker: Job {job.JobId} status changed to {status}")
        
        # Validate configuration
        if not apiEndpoint:
            self.LogInfo("APIEndpoint not configured!")
            return
        if not tenantId:
            self.LogInfo("TenantId not configured!")
            return

        try:
            url = f"http://{apiEndpoint}:{apiPort}/{tenantId}/renders"
            headers = {
                "Content-Type": "application/json"
            }
            
            data = {
                "job_comment": job.JobComment,
                "job_complete_time": job.JobCompletedDateTime.ToString(),
                "job_department": job.JobDepartment,
                "job_id": job.JobId,
                "job_name": job.JobName,
                "job_plugin": job.JobPlugin,
                "job_status": status,
                "job_start_time": job.JobStartedDateTime.ToString(),
                "job_submit_time": job.JobSubmitDateTime.ToString(),
                "job_user_name": job.JobUserName,
                "tenant_id": job.JobExtraInfo0,
                "parent_id": job.JobExtraInfo1,
                "package_name": job.JobExtraInfo2,
                "job_submit_machine": job.JobSubmitMachine,
                "job_input_path": job.GetJobPluginInfoKeyValue('InputPath'),
                "job_output_path": job.GetJobPluginInfoKeyValue('OutputPath'),
                "job_preset_file": job.GetJobPluginInfoKeyValue('PresetFile'),
                "job_total_render_time": job.TotalRenderTime.ToString(),
                "job_completed_frames": job.CompletedFrames,
            }
            
            response = requests.post(url, headers=headers, data=json.dumps(data))
            
            # Log response for debugging
            self.LogInfo(f"API Response: {response.status_code} - {response.text}")
            
            if response.status_code != 200:
                self.LogInfo(f"API returned non-200 status: {response.status_code}")

        except Exception as e:
            self.LogInfo(f"Error while sending job data for JobId {job.JobId}: {str(e)}")
            # Also print to stdout for additional debugging
            print(f"ZephyrTracker Error: {str(e)}")