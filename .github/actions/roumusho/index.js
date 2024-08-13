const core = require('@actions/core');
const github = require('@actions/github');
const fs = require('fs');

async function run() {
  try {
    const token = core.getInput('GITHUB_TOKEN');
    const issueNumber = core.getInput('ISSUE_NUMBER');
    const commentBody = core.getInput('COMMENT_BODY');
    const octokit = github.getOctokit(token);
    const context = github.context;

    if (commentBody.startsWith('/remind')) {
      await octokit.rest.reactions.createForIssueComment({
        owner: context.repo.owner,
        repo: context.repo.repo,
        issue_number: issueNumber,
        content: '+1'
      });

      const timestamp = Date.now();
      const filename = `reminder_${issueNumber}_${timestamp}.txt`;
      fs.writeFileSync(filename, commentBody);
    }
  } catch (error) {
    core.setFailed(error.message);
  }
}

run();
