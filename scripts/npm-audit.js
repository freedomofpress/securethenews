#!/usr/bin/env node

let path = require('path')
let program = require('commander')

// Import a "promisified" version of `exec` so we can use it procedurally
// with `await`
let { promisify } = require('util')
let exec = promisify(require('child_process').exec)

// Simple functions to escape strings for use in XML templates. These wouldn't
// be sufficient for any complex purpose, but for transforming npm audit output
// to XML, these should be fine
const escapeDoubleQuotes = s => s.replace('"', '\"')
const escapeAngleBrackets = s => s.replace('<', '\<').replace('>', '\>')


// START TEMPLATE: Generate a human-readable title from an advisory object
const advisoryTitleTemplate = advisoryObj => `${advisoryObj.severity.toUpperCase()}: ${advisoryObj.id} - ${advisoryObj.title}`
// END TEMPLATE


// START TEMPLATE: take an advisory object and render a human-readable display
const advisoryTemplate = advisoryObj => `${advisoryObj.overview}

${advisoryObj.recommendation}

Version:   ${advisoryObj.findings[0].version}
Path:      ${advisoryObj.findings[0].paths[0]}
More info: ${advisoryObj.url}`
// END TEMPLATE


// START TEMPLATE: take a list of recommended actions as well as info about
// which advisories are ignored and generate a human-readable display
const summaryTemplate = (actions, passThruIds, ignoredIds) => `Summary

Advisories: ${passThruIds.length}
Ignored:    ${ignoredIds.length}
${actions.length > 0 ? (
	'\nRecommended Actions\n\n' +
	actions.map(action => `Run \`npm ${action.action} ${action.module}@${action.target}\` to resolve these advisories: ${action.resolves.map(x => x.id).join(', ')}`).join('\n')
): ''}`
// END TEMPLATE


program
	.description('Run npm audit with customized output')
	.option('-i, --ignore <ids>', 'Vulnerability IDs to ignore')
	.option('-x, --xml', 'Output as JUnit-formatted XML')
	.action(async function(options) {
		let exceptionIds = []

		// If advisories to ignore are specified in command invocation, parse them
		// into an array
		if (options && options.ignore) {
			// If ignore ids are specified, split them into an array of ints
			exceptionIds = options.ignore.split(',').map(id => parseInt(id))
		}

		// Run `npm audit` and capture output. We use a try/catch to capture
		// output regardless of whether the audit returns zero or not
		let stdout, stderr
		try {
			// Exterior parens necessary for variable unpacking without declaration
			// (i.e., without var/let/const)
			({ stdout, stderr } = await exec(
				'npm audit --json',
				{ cwd: path.dirname(__dirname) }
			))
		} catch(error) {
			// See above
			({ stdout, stderr } = error)
		}

		const results = JSON.parse(stdout)
		const advisories = results.advisories
		// List of IDs filtered to the ones that are marked for display
		const passThruAdvisoriesIds = Object.keys(results.advisories).filter(x => !exceptionIds.includes(parseInt(x)))
		// List of IDs filtered to ones that are being ignored
		const ignoredAdvisoriesIds = Object.keys(results.advisories).filter(x => exceptionIds.includes(parseInt(x)))

		// Filter actions to ones that resolve advisories that passed the filter
		// Basically we're checking each action's list of advisories it resolves
		// for overlap with our `passThruAdvisoriesIds`. If theres any overlap, we
		// keep the action. Otherwise we ignore it.
		const passThruActions = results.actions.filter(
			action => action.resolves.some(
				resolveObj => passThruAdvisoriesIds.includes(resolveObj.id.toString())
			)
		)

		if (options && options.xml) {
			// If the command was invoked with the XML argument, output as XML
			const junitXML = `\
<?xml version="1.0" encoding="UTF-8"?>
<testsuites>
	<testsuite name="NPM Audit Summary">
		${(passThruActions.length > 0) && `
			<testcase name="Summary">
				<failure message="Summary">
<![CDATA[
${summaryTemplate(passThruActions, passThruAdvisoriesIds, ignoredAdvisoriesIds)}
]]>
				</failure>
			</testcase>
		`}
	</testsuite>
	<testsuite name="NPM Audit Advisories">
			${passThruAdvisoriesIds.map(id => `\
				<testcase name="${escapeDoubleQuotes(advisoryTitleTemplate(advisories[id]))}">
					<failure message="${escapeDoubleQuotes(advisories[id].title)}" type="${escapeDoubleQuotes(advisories[id].severity).toUpperCase()}">
<![CDATA[
${advisoryTemplate(advisories[id])}
]]>
					</failure>
				</testcase>
			`).join('')}
	</testsuite>
</testsuites>
			`
			console.log(junitXML)
		} else {
			// If the command was invoked without the XML argument, output in
			// human-readable format with pretty dividers
			const hr = '-'.repeat(process.stdout.columns)
			const hr2 = '='.repeat(process.stdout.columns)
			const title = 'NPM Audit Security Report'
			const leftPad = ' '.repeat(Math.floor((process.stdout.columns - title.length) / 2))
			let consoleOutput = '\n' + leftPad + title + '\n\n'
			consoleOutput += hr2 + '\n\n'
			consoleOutput += summaryTemplate(passThruActions, passThruAdvisoriesIds, ignoredAdvisoriesIds) + '\n\n'
			consoleOutput += hr + '\n\n'
			consoleOutput += passThruAdvisoriesIds.map(id => [
				advisoryTitleTemplate(advisories[id]),
				advisoryTemplate(advisories[id]),
				hr
			].join('\n\n')).join('\n\n')
			console.log(consoleOutput)
		}

		// If any advisories were caught, exit non-zero
		if (passThruAdvisoriesIds.length > 0) process.exit(1)
	})

program.parse(process.argv)
