"use strict";

const { contributionTotals, fail, graphql, utcNow } = require("./github");

function expCdf(value) {
  return 1 - 2 ** (-value);
}

function logCdf(value) {
  return value ? value / (1 + value) : 0;
}

function level(commits, pulls, issues, reviews, stars, followers) {
  const score = (
    2 * expCdf(commits / 250)
    + 3 * expCdf(pulls / 50)
    + expCdf(issues / 25)
    + expCdf(reviews / 2)
    + 4 * logCdf(stars / 50)
    + logCdf(followers / 10)
  );
  const percent = (1 - score / 12) * 100;
  const steps = [1, 12.5, 25, 37.5, 50, 62.5, 75, 87.5, 100];
  const names = ["S", "A+", "A", "A-", "B+", "B", "B-", "C+", "C"];
  for (let index = 0; index < steps.length; index += 1) {
    if (percent <= steps[index]) return names[index];
  }
  return "C";
}

async function load(login) {
  const data = await contributionTotals(login);
  const counts = new Map();
  for (const [day, count] of data.days) {
    const year = day.slice(0, 4);
    counts.set(year, (counts.get(year) || 0) + count);
  }
  const years = [];
  for (let year = data.created.getUTCFullYear(); year <= utcNow().getUTCFullYear(); year += 1) {
    years.push([String(year), counts.get(String(year)) || 0]);
  }
  const query = `
    query($login: String!) {
      user(login: $login) {
        followers { totalCount }
        issues { totalCount }
        pullRequests { totalCount }
        repositoriesContributedTo(
          first: 1
          contributionTypes: [COMMIT, ISSUE, PULL_REQUEST, REPOSITORY]
        ) { totalCount }
        contributionsCollection {
          totalCommitContributions
          restrictedContributionsCount
          totalPullRequestReviewContributions
        }
      }
    }
    `;
  const user = (await graphql(query, { login })).user;
  if (!user) fail("no github user named " + login);
  const year = user.contributionsCollection;
  const commits = year.totalCommitContributions + (year.restrictedContributionsCount || 0);
  const pulls = user.pullRequests.totalCount;
  const issues = user.issues.totalCount;
  const reviews = year.totalPullRequestReviewContributions;
  const followers = user.followers.totalCount;
  return {
    login: data.login,
    years: years.slice(-8),
    rank: level(commits, pulls, issues, reviews, data.stars, followers),
    stars: data.stars,
    commits,
    pulls,
    issues,
    reviews,
    followers,
    contributed: user.repositoriesContributedTo.totalCount,
  };
}

module.exports = { load };
