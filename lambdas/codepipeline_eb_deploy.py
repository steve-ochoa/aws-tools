import logging
import boto3

logger = logging.getLogger(__name__)


def get_revision_summary(pipeline_name, revision_id):
    """Retrurns revisionSummary associated with revision_id

    Gets list of pipeline executions and evaluates each one until it finds
    one with the same revisionId. Then extracts the revisionSummary from it.
    """
    codepipeline = boto3.client('codepipeline')
    pipeline_executions = codepipeline.list_pipeline_executions(
        pipelineName=pipeline_name
    )
    execution_summaries = pipeline_executions['pipelineExecutionSummaries']
    revision_summary = None
    for execution in execution_summaries:
        source_revisions = execution['sourceRevisions']
        for revision in source_revisions:
            source_revision_id = revision['revisionId']
            if source_revision_id == revision_id:
                revision_summary = revision['revisionSummary'][:199]
                break
    if revision_summary is None:
        logger.error("Unable to find pipeline execution containing "
                     "revisionId {}. Setting revision_summary to "
                     "empty.".format(revision_id))
        revision_summary = ""
    return revision_summary


def lambda_handler(event, context):
    codepipeline = boto3.client('codepipeline')
    job_id = event['CodePipeline.job']['id']
    job_data = event['CodePipeline.job']['data']
    # Check to make sure only a single artifact
    artifact_revision_id = job_data['inputArtifacts'][0]['revision']
    get_job_details = codepipeline.get_job_details(jobId=job_id)
    pipeline_context = get_job_details['jobDetails']['data']['pipelineContext']
    pipeline_name = pipeline_context['pipelineName']
    print(artifact_revision_id)
    print(pipeline_name)
    codepipeline.put_job_success_result(jobId=job_id)
