store
=====
store is a web service for storing data that will automatically get deleted on its set expiry date.

API
---

### Endpoints

<table>
	<thead>
		<tr>
			<th>Endpoint</th>
			<th>Description</th>
			<th>Methods</th>
		</tr>
	</thead>
	<tbody>
		<tr>
			<td><code>/api/**/</code></td>
			<td>Requests ending in a <code>/</code> are namespace endpoints. Namespaces efficiently store sets of data by key/alias.</td>
			<td>
				<table>
					<tr>
						<td><code>GET</code></td>
						<td>A get request returns a JSON list of keys/aliases in that namespace.</td>
					</tr>
					<tr>
						<td><code>POST</code></td>
						<td>A post request creates an entry and returns the JSON object and a new <code>Location</code> header.</td>
					</tr>
				</table>
			</td>
		</tr>
		<tr>
			<td><code>/api/**/*</code></td>
			<td>Requests ending in an key/alias are entry endpoints. Entries are key/alias indexed JSON objects containing metadata of stored information.</td>
			<td>
				<table>
					<tr>
						<td><code>GET</code></td>
						<td>A get request returns a JSON object of that entry.</td>
					</tr>
					<tr>
						<td><code>PUT</code></td>
						<td>A put request either creates an entry at the specified alias if it does not exist or updates the expiry date of the existing object and returns the JSON object.</td>
					</tr>
					<tr>
						<td><code>DELETE</code></td>
						<td>A delete request deletes the entry and its associated data.</td>
					</tr>
				</table>
			</td>
		</tr>
		<tr>
			<td><code>/store/**/*</code></td>
			<td>Requests represent the actual data in the store.</td>
			<td>
				<table>
					<tr>
						<td><code>GET</code></td>
						<td>A get request returns the stored data with its metadata encoded in headers.</td>
					</tr>
					<tr>
						<td><code>PUT</code></td>
						<td>A put request updates the data in the resource. Note: The size and type given must match those in the <code>/api/</code> entry.</td>
					</tr>
				</table>
			</td>
		</tr>
	</tbody>
</table>

### Payload

```json
{"filename": "example.txt", "size": 144, "type": "text/plain", "expire": 2147483647, "locked": true}
```

### Response

```json
{"alias": "abcd", "date": "1474826615", "filename": "example.txt", "size": "144", "type": "text/plain", "expire": 2147483647, "locked": true}
```
