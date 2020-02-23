const fs = require('fs')
const path = require('path')
const assert = require('assert')
const util = require('util')

const endsWithTxt = /^.*\.txt$/
const readFilePromise = util.promisify(fs.readFile)

function walkDir(dir, callback) {
	fs.readdirSync(dir).forEach(f => {
		let dirPath = path.join(dir, f)
		let isDirectory = fs.statSync(dirPath).isDirectory()
		isDirectory
			?
			walkDir(dirPath, callback) :
			callback(path.join(dir, f))
	})
}

const findDuplicateInArray = (arr) => {
	const counter = {}

	for (const entry of arr)
		counter[entry] = counter[entry] !== undefined ? counter[entry] + 1 : 1

	return Object.entries(counter).filter(([entry, count]) => count > 1).map(([entry, count]) => entry)
}

walkDir(__dirname, async (filename) => {
	// Not a txt file
	if (!endsWithTxt.test(filename)) return

	// Read the file
	const file = await readFilePromise(filename, 'utf8')

	// Each line of the file to an array removing the empty lines
	const lines = file.split('\n').filter(entry => entry !== '')

	// If the size of the set differs form the one of the array it means there are duplicates
	const set = new Set(lines)
	try {
		assert.equal(lines.length, set.size, `Duplicate found`)
	} catch (e) {
		console.log(`Duplicate in ${path.basename(filename)}: ${findDuplicateInArray(lines)}`)
	}
})
